# -*- coding: utf-8 -*-
"""tri-code-analyzer 阶段 2 确定性栈探测器（可选预检）。

把 references/tech-stacks/INDEX.md 的「主信号必中 + 辅信号加权」分级语义落为
可复现的确定性脚本，消除模型纯读表判定时的 AND/OR 歧义（原 tri-code-analyzer
v1.3.1 的根因：AND 读法漏判 5 个官方脚手架栈，OR 读法误判 2 个栈）。

设计要点（与 INDEX.md 严格对应）：
- 每行「主信号」全部命中即选定该栈；「辅信号」仅用于细化子栈/打包方式，不影响命中。
- 多栈主信号同时命中时，全部读卡（与 INDEX.md 规则 1 一致），不取首个。
- 通用后端行：原索引信号「按卡内信号分表匹配」不可 grep，致 spring/fastapi/go
  掉「未覆盖栈」触发联网建已存在的卡。本脚本把通用后端主信号上提为可 grep 的
  清单文件 / 框架入口 token。
  * 设计细化（已在最终验证报告披露）：package.json 同时是前端与后端工程的清单，
    裸 package.json 不足以判定为后端；故通用后端仅在「后端专属清单文件」或
    「框架入口 token」命中时成立，避免 Taro/RN/Electron 等前端工程被误挂后端卡。

用法：
    python scripts/stack_detect.py <repo> [--json] [--verbose]

退出码：脚本正常运行一律 0；无任何栈命中时在报告中标注「未命中 → 走 acquire 协议」。
"""
import os
import sys
import json
import glob

# 索引表顺序与栈卡文件名（与 INDEX.md 一致）
STACK_ORDER = [
    "ArkTS / HarmonyOS",
    "Electron",
    "Flutter / Dart",
    "Qt / C++",
    "React Native",
    "Taro",
    "uni-app / uni-app x",
    "Agent Skills 插件",
    "通用后端",
]

CARD_FILE = {
    "ArkTS / HarmonyOS": "arkts.md",
    "Electron": "electron.md",
    "Flutter / Dart": "flutter.md",
    "Qt / C++": "qt.md",
    "React Native": "react-native.md",
    "Taro": "taro.md",
    "uni-app / uni-app x": "uni-app.md",
    "Agent Skills 插件": "agent-skills-plugin.md",
    "通用后端": "generic-backend.md",
}

SRC_EXTS = (
    ".py", ".java", ".kt", ".go", ".js", ".ts", ".tsx", ".jsx",
    ".cs", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".m", ".mm", ".rb",
    ".php", ".rs", ".scala", ".groovy",
)

FRAMEWORK_ENTRY_TOKENS = (
    "@SpringBootApplication",
    "FastAPI(",
    "Flask(__name__)",
    "gin.Engine",
    "express(",
    "@Module(",
    # 注：.NET 后端以 *.csproj 清单文件（BACKEND_MANIFESTS）判定，不再用 "Program.cs"
    # 这种文件名片段做子串匹配——它会误中探测器自身源码、文档与任意提及该文件名的文本。
)

# 扫描时跳过的目录（仓库元数据 / 依赖 / 缓存 / 构建产物），避免噪声与自匹配
IGNORE_DIRS = {
    ".git", "__pycache__", ".tribro", "node_modules", ".venv", "venv",
    "dist", "build", ".idea", ".vscode", "target", ".ruff_cache", ".mypy_cache",
}

# 探测器自身的源码文件（内含框架入口 token 字符串列表），必须排除，否则会自匹配
SKIP_FILES = {"stack_detect.py"}

BACKEND_MANIFESTS = (
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "go.mod",
    "requirements.txt",
    "pyproject.toml",
    "Cargo.toml",
    # *.csproj 用扩展名匹配，见 has_csproj
)


# --------------------------------------------------------------------------- #
# 通用文件/内容探测原语
# --------------------------------------------------------------------------- #
def exists(root, rel):
    return os.path.isfile(os.path.join(root, rel))


def _walk(root):
    """yield (dirpath, filename)，跳过 IGNORE_DIRS（仓库元数据/依赖/缓存/构建产物）。"""
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in IGNORE_DIRS]
        for f in fn:
            yield dp, f


def has_ext(root, ext):
    for _dp, f in _walk(root):
        if f.endswith(ext):
            return True
    return False


def has_named(root, names):
    for _dp, f in _walk(root):
        if f in names:
            return True
    return False


def has_csproj(root):
    for _dp, f in _walk(root):
        if f.endswith(".csproj"):
            return True
    return False


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except Exception:
        return ""


def read_json_safe(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return json.load(fh)
    except Exception:
        return None


def _grep_tokens_in_repo(root, tokens):
    for dp, f in _walk(root):
        if f in SKIP_FILES:
            continue
        if not f.endswith(SRC_EXTS):
            continue
        txt = read_text(os.path.join(dp, f))
        if not txt:
            continue
        for tok in tokens:
            if tok in txt:
                return True
    return False


def package_has_dep(root, name, where=("dependencies", "devDependencies")):
    data = read_json_safe(os.path.join(root, "package.json"))
    if not isinstance(data, dict):
        return False
    for sec in where:
        section = data.get(sec)
        if isinstance(section, dict) and name in section:
            return True
    return False


def has_yaml_frontmatter(path):
    """SKILL.md 类文件：首行 --- 且其后（前 64 行内）再次出现 ---（YAML frontmatter 闭合）。"""
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            lines = []
            for i, ln in enumerate(fh):
                lines.append(ln.rstrip("\n"))
                if i >= 63:
                    break
    except Exception:
        return False
    if not lines or lines[0].strip() != "---":
        return False
    # 首行之后、前 64 行内再次出现独立的 --- 即视为有 YAML frontmatter
    return any(ln.strip() == "---" for ln in lines[1:64])


# --------------------------------------------------------------------------- #
# 每栈「主信号」判定（返回 (命中: bool, 缺信号清单: list[str])）
# 主信号全部命中 -> 选定该栈；辅信号缺失仅记录，不影响命中。
# --------------------------------------------------------------------------- #
def primary_arkts(root):
    miss = []
    has_mod = has_ext(root, "module.json5")
    has_ets = has_ext(root, ".ets")
    has_ohpkg = exists(root, "oh-package.json5")
    if not has_mod:
        miss.append("module.json5")
    if not has_ets:
        miss.append(".ets 文件")
    cond_a = has_mod and has_ets
    if not cond_a and not has_ohpkg:
        if not has_ohpkg:
            miss.append("oh-package.json5")
        return False, miss
    return True, []


def primary_electron(root):
    if package_has_dep(root, "electron", where=("devDependencies", "dependencies")):
        return True, []
    return False, ["devDependencies 含 electron"]


def primary_flutter(root):
    pub = read_text(os.path.join(root, "pubspec.yaml"))
    has_flutter_dep = bool(pub) and ("sdk: flutter" in pub or "flutter:" in pub
                                     or "flutter_test" in pub or '"flutter"' in pub)
    has_dart = has_ext(root, ".dart")
    if has_flutter_dep or has_dart:
        return True, []
    miss = []
    if not has_flutter_dep:
        miss.append("pubspec.yaml 含 flutter 依赖")
    if not has_dart:
        miss.append(".dart 文件")
    return False, miss


def primary_qt(root):
    has_pro = has_ext(root, ".pro")
    has_qml = has_ext(root, ".qml")
    has_cmake_qt = False
    for dp, f in _walk(root):
        if f == "CMakeLists.txt":
            if "Qt" in read_text(os.path.join(dp, f)):
                has_cmake_qt = True
    if has_pro or has_qml or has_cmake_qt:
        return True, []
    miss = []
    if not has_pro:
        miss.append(".pro 文件")
    if not has_cmake_qt:
        miss.append("CMakeLists.txt 含 Qt")
    if not has_qml:
        miss.append("*.qml 文件")
    return False, miss


def primary_react_native(root):
    if package_has_dep(root, "react-native", where=("dependencies", "devDependencies")):
        return True, []
    return False, ["依赖含 react-native"]


def primary_taro(root):
    if package_has_dep(root, "@tarojs/taro", where=("dependencies", "devDependencies")):
        return True, []
    return False, ["依赖含 @tarojs/taro"]


def primary_uniapp(root):
    has_manifest = exists(root, "manifest.json")
    has_pages = exists(root, "pages.json")
    if has_manifest and has_pages:
        return True, []
    miss = []
    if not has_manifest:
        miss.append("manifest.json")
    if not has_pages:
        miss.append("pages.json")
    return False, miss


def primary_agent_skills(root):
    # 主信号：插件形态 skills/*/SKILL.md（YAML frontmatter）OR 单技能形态根目录 SKILL.md（YAML frontmatter）
    candidates = glob.glob(os.path.join(root, "skills", "*", "SKILL.md"))
    valid = [c for c in candidates if has_yaml_frontmatter(c)]
    root_skill = os.path.join(root, "SKILL.md")
    if not valid and os.path.isfile(root_skill) and has_yaml_frontmatter(root_skill):
        valid = [root_skill]
    if valid:
        return True, []
    miss = []
    if not candidates:
        miss.append("skills/*/SKILL.md")
    else:
        miss.append("skills/*/SKILL.md 含 YAML frontmatter")
    if not os.path.isfile(root_skill):
        miss.append("根目录 SKILL.md")
    # 辅信号提示
    aux = []
    if not exists(root, os.path.join(".claude-plugin", "plugin.json")):
        aux.append(".claude-plugin/plugin.json")
    if not exists(root, os.path.join("hooks", "session-start")):
        aux.append("hooks/session-start")
    return False, miss


def primary_generic_backend(root):
    # 后端专属清单文件（不含裸 package.json，避免前端误挂）
    manifest_hit = False
    miss = []
    for m in BACKEND_MANIFESTS:
        if has_named(root, {m}):
            manifest_hit = True
            break
    if has_csproj(root):
        manifest_hit = True
    entry_hit = _grep_tokens_in_repo(root, FRAMEWORK_ENTRY_TOKENS)
    # 兜底：package.json 存在且含后端框架入口 token 也算
    pkg_entry = False
    if exists(root, "package.json"):
        pkg_txt = read_text(os.path.join(root, "package.json"))
        if any(tok.split("(")[0] in pkg_txt for tok in ("express(", "@Module(", "gin.Engine")):
            pkg_entry = True
    if manifest_hit or entry_hit or pkg_entry:
        return True, []
    if not manifest_hit:
        miss.append("后端清单文件(pom.xml/build.gradle/go.mod/requirements.txt/pyproject.toml/*.csproj/Cargo.toml)")
    if not entry_hit and not pkg_entry:
        miss.append("框架入口 token(@SpringBootApplication/FastAPI()/Flask(__name__)/gin.Engine/express()/@Module()/Program.cs)")
    return False, miss


PRIMARY_FNS = {
    "ArkTS / HarmonyOS": primary_arkts,
    "Electron": primary_electron,
    "Flutter / Dart": primary_flutter,
    "Qt / C++": primary_qt,
    "React Native": primary_react_native,
    "Taro": primary_taro,
    "uni-app / uni-app x": primary_uniapp,
    "Agent Skills 插件": primary_agent_skills,
    "通用后端": primary_generic_backend,
}


# --------------------------------------------------------------------------- #
# 辅信号（仅细化 / 报告，不影响命中）
# --------------------------------------------------------------------------- #
def aux_signals(root, stack):
    if stack == "ArkTS / HarmonyOS":
        return ["entry/src/main"] if not exists(root, os.path.join("entry", "src", "main")) else []
    if stack == "Electron":
        aux = []
        if not package_has_dep(root, "electron-builder"):
            aux.append("electron-builder")
        if not package_has_dep(root, "@electron-forge/cli") and not package_has_dep(root, "electron-forge"):
            aux.append("@electron-forge/cli 或 electron-forge")
        if not has_named(root, {"main.js", "main.ts", "main.mjs", "src/index.js"}):
            aux.append("主进程入口 main.js|ts|src/index.js")
        return aux
    if stack == "Flutter / Dart":
        return ["lib/main.dart"] if not exists(root, os.path.join("lib", "main.dart")) else []
    if stack == "Qt / C++":
        aux = []
        if not _grep_tokens_in_repo(root, ("Q_OBJECT",)):
            aux.append("Q_OBJECT 宏")
        if not _grep_tokens_in_repo(root, ("#include <Q",)):
            aux.append("#include <Q...>")
        return aux
    if stack == "React Native":
        aux = []
        if not has_named(root, {"react-native.config.js"}):
            aux.append("react-native.config.js")
        if not (exists(root, "ios") and exists(root, "android")):
            aux.append("ios/ + android/ 目录")
        return aux
    if stack == "Taro":
        return ["config/index.js(ts)"] if not (exists(root, os.path.join("config", "index.js"))
                                                or exists(root, os.path.join("config", "index.ts"))) else []
    if stack == "uni-app / uni-app x":
        aux = []
        if not package_has_dep(root, "@dcloudio/uni-app"):
            aux.append("依赖含 @dcloudio/uni-app")
        if not has_ext(root, ".uvue"):
            aux.append(".uvue 文件")
        return aux
    if stack == "Agent Skills 插件":
        aux = []
        if not exists(root, os.path.join(".claude-plugin", "plugin.json")):
            aux.append(".claude-plugin/plugin.json")
        if not exists(root, os.path.join("hooks", "session-start")):
            aux.append("hooks/session-start")
        if not any(exists(root, d) for d in (".opencode", ".pi", ".gemini", ".hermes-plugin")):
            aux.append("平台适配器目录(.opencode/.pi/.gemini/.hermes-plugin)")
        return aux
    if stack == "通用后端":
        # 子栈提示：哪种后端清单/入口命中
        hints = []
        for m in BACKEND_MANIFESTS:
            if has_named(root, {m}):
                hints.append(m)
        if has_csproj(root):
            hints.append("*.csproj")
        for tok in FRAMEWORK_ENTRY_TOKENS:
            if _grep_tokens_in_repo(root, (tok,)):
                hints.append(tok)
        return hints
    return []


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
def detect(root):
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        raise SystemExit("错误：仓库路径不存在或不是目录：%s" % root)
    hits = []
    details = []
    for stack in STACK_ORDER:
        hit, miss = PRIMARY_FNS[stack](root)
        if hit:
            aux = aux_signals(root, stack)
            hits.append(stack)
            details.append({
                "stack": stack,
                "card": CARD_FILE[stack],
                "primary": "命中",
                "missing_aux": aux,
            })
    if not hits:
        return {
            "repo": root,
            "hit": False,
            "stacks": [],
            "cards": [],
            "note": "未命中任何已建卡栈 → 走 acquire-unknown-stack.md 获取协议",
            "details": [],
        }
    return {
        "repo": root,
        "hit": True,
        "stacks": hits,
        "cards": [CARD_FILE[s] for s in hits],
        "note": "主栈取首命中构建产物目标平台；多栈命中全部读卡",
        "details": details,
    }


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    repo = args[0]
    as_json = "--json" in args
    verbose = "--verbose" in args
    try:
        result = detect(repo)
    except SystemExit as e:
        print(str(e))
        return 2

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print("=" * 64)
    print("仓库：%s" % result["repo"])
    if not result["hit"]:
        print("结果：未命中任何已建卡栈")
        print("处置：%s" % result["note"])
        print("=" * 64)
        return 0
    print("命中栈（%d）：%s" % (len(result["stacks"]), " / ".join(result["stacks"])))
    print("读卡：%s" % " / ".join(result["cards"]))
    print("-" * 64)
    for d in result["details"]:
        print("• %s  [%s]" % (d["stack"], d["card"]))
        if verbose or d["missing_aux"]:
            print("    辅信号缺失（仅细化，不影响命中）：%s"
                  % ("、".join(d["missing_aux"]) if d["missing_aux"] else "（全中）"))
    print("=" * 64)
    return 0


if __name__ == "__main__":
    sys.exit(main())
