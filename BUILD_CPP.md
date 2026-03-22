# 编译 C++ 程序说明 (待完善)

## 目录

- [工具简介](#工具简介)
- [前置依赖与安装](#前置依赖与安装)
  - [macOS](#macos)
  - [Ubuntu / Debian](#ubuntu--debian)
  - [Windows](#windows)
- [编译步骤](#编译步骤)
  - [Linux / macOS](#linux--macos)
  - [Windows](#windows-1)
- [各题编译与运行](#各题编译与运行)

---

## 工具简介

### CMake

[CMake](https://cmake.org/) 是一个跨平台的构建系统生成工具。它本身不直接编译代码，而是读取项目根目录下的 `CMakeLists.txt` 文件，然后为当前平台生成对应的构建文件（Linux/macOS 上生成 Makefile，Windows 上生成 Visual Studio 工程或 Ninja 构建文件）。有了 CMake，同一份配置文件就能在不同操作系统上无缝编译。

### vcpkg

[vcpkg](https://vcpkg.io/) 是微软开发的 C++ 包管理器，用于在 Windows（以及 Linux/macOS）上方便地安装 C++ 第三方库。它能自动下载、编译并配置 OpenCV 等库，并与 CMake 无缝集成——只需在 `cmake` 命令中指定一个工具链文件路径，CMake 就能自动找到 vcpkg 安装的所有库，无需手动设置头文件或链接路径。

### OpenCV

[OpenCV](https://opencv.org/)（Open Source Computer Vision Library）是一个开源的计算机视觉与图像处理库。本作业中的 C++ 程序主要利用 OpenCV 进行图像可视化和 简单的GUI 交互（窗口显示、鼠标点击、绘图等）。

### Visual Studio Build Tools（仅 Windows）

[Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022) 提供 Windows 上的 MSVC C++ 编译器和链接器，是在 Windows 上编译 C++ 代码的必要工具链。它是 Visual Studio IDE 的"纯命令行"子集，体积远小于完整 IDE，安装时勾选「使用 C++ 的桌面开发」即可。

### VS Code + CMake Tools 扩展

在 VS Code 中安装 **CMake Tools** 扩展后，编辑器底部会出现工具栏，可以一键完成配置（`cmake -B build ...`）和编译（`cmake --build build ...`），无需在终端手动输入命令，适合日常开发使用。

P.S. 强烈建议Windows用户参考官方教程：https://learn.microsoft.com/zh-cn/vcpkg/get_started/get-started-vscode?pivots=shell-powershell 

---

## 前置依赖与安装

| 工具 | 最低版本 | 说明 |
|------|----------|------|
| CMake | 3.15 | 构建系统 |
| C++ 编译器 | C++17 | GCC 9+ / Clang 10+ / MSVC 2019+ |
| OpenCV | 4.x | 图像处理与 GUI |

### macOS

使用 [Homebrew](https://brew.sh/) 一键安装：

```bash
# 首次安装需要一段时间下载编译
brew install cmake opencv
```

### Ubuntu / Debian

```bash
# 首次安装需要一段时间下载编译
sudo apt install cmake libopencv-dev
```

### Windows

**第一步：安装 MSVC 编译器**

下载并运行 [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)，在安装界面勾选「**使用 C++ 的桌面开发**」工作负载，然后点击安装。

**第二步：安装 CMake**

从 [cmake.org/download](https://cmake.org/download/) 下载 Windows 安装包，安装时勾选「**Add CMake to the system PATH**」。

**第三步：安装 vcpkg 和 OpenCV**

在 PowerShell 中依次执行：

```powershell
# 克隆 vcpkg 到 C:\vcpkg
git clone https://github.com/microsoft/vcpkg.git C:\vcpkg

# 初始化 vcpkg
C:\vcpkg\bootstrap-vcpkg.bat

# 安装 OpenCV（x64，首次安装需要一段时间下载编译）
C:\vcpkg\vcpkg.exe install opencv4:x64-windows

# 与 CMake 全局集成（只需执行一次）
C:\vcpkg\vcpkg.exe integrate install
```

---

## 编译步骤

### Linux / macOS

以 op_1 为例（其他题目同理，进入对应的 `code_template_cpp/` 目录执行即可）：

```bash
cd hw_1/op_1/code_template_cpp
mkdir build && cd build
cmake ..
make -j4
```

### Windows

在 PowerShell 中执行（以 hw_1/op_1 为例）：

```powershell
cd hw_1\op_1\code_template_cpp
cmake -B build -DCMAKE_TOOLCHAIN_FILE=C:\vcpkg\scripts\buildsystems\vcpkg.cmake
cmake --build build --config Release --parallel 4
```
注意这里的 DCMAKE_TOOLCHAIN_FILE是默认你的vcpkg安装路径为`C:\vcpkg` , 如果你的 vcpkg 不在 `C:\vcpkg`，将路径替换为实际安装位置即可。

> **`-DCMAKE_TOOLCHAIN_FILE` 是什么？**
>
> CMake 在配置项目时，需要知道去哪里寻找第三方库（头文件、`.lib`/`.dll` 等）。
> `CMAKE_TOOLCHAIN_FILE` 是一个 CMake 变量，用来指定一个"工具链文件"——本质上是一段
> CMake 脚本，在配置开始时自动执行，告诉 CMake 如何找到编译器和依赖库。
>
> vcpkg 提供了自己的工具链文件 `vcpkg.cmake`，将它传给 CMake 后，CMake 就会自动在
> vcpkg 的安装目录中搜索所有已安装的库（包括 OpenCV），不再需要手动设置任何路径。
>
> 命令中的 `-D` 前缀是 CMake 定义变量的通用语法，即 `-D变量名=值`。


**使用 VS Code 中的CMake插件编译（推荐）：**

1. 安装 VS Code 扩展 **CMake Tools**。

![](./imgs/CMakeTools.png)

2. 用 VS Code 打开文件夹（例如 `hw_1/`）。
3. 在弹出的提示中选择编译器工具链（MSVC x64）。
4. 点击底部状态栏的 **Build** 按钮，等待编译完成。

编译完成后，可执行文件会输出到各自的源码目录，便于访问相对路径的数据文件。

---

## 各题编译与运行

每道题的 `code_template_cpp/` 目录下均有独立的 `CMakeLists.txt`。使用命令行，或者用 VS Code 打开该目录使用CMake Tools即可独立编译。具体的编译命令、运行方式和 GUI 操作说明请查阅各题的 README（C++ 框架 一节）：

- [x] [op_1 说明](hw_1/op_1/README.md#c-框架) — 接缝裁剪（Seam Carving）
- [x] [op_2 说明](hw_1/op_2/README.md#c-框架) — 地铁最短路径（Dijkstra）
- [ ] [op_3 说明](hw_1/op_3/README.md#c-框架) — 社交网络关键节点识别（尚未实现）
