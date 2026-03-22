# 选项1：图像的接缝裁剪

## 目录

- [引言](#引言)
- [实验要求](#实验要求)
- [MATLAB 框架](#matlab-框架)
  - [运行方式](#运行方式)
  - [需要完成的代码](#需要完成的代码)
- [Python 框架](#python-框架)
  - [环境配置](#环境配置)
  - [文件结构](#文件结构)
  - [运行方式](#运行方式-1)
  - [需要完成的代码](#需要完成的代码-1)
- [C++ 框架](#c-框架)
  - [需要完成的代码](#需要完成的代码-2)
  - [编译](#编译)
  - [运行方式](#运行方式-2)
  - [GUI 说明](#gui-说明)

## 引言

打开 bing 浏览器首页并全屏，你会看到类似于下图的首页背景图片

<p align="center">
    <img src="./figs/bing1.png" height=300>
</p>

这时候如果你改变浏览器窗口的大小（比如缩小窗口的长度），你会看到首页背景图片变成下下面这样

<p align="center">
    <img src="./figs/bing2.png" height=300>
</p>

如你所料，背景图片的尺寸随着窗口大小发生变化。但仔细观察，不难发现**这两张图片并不是简单的裁剪（chopping）或者缩放（rescaling）的关系**。

事实上，在图像处理领域，常常会遇到需要改变给定图像的长宽比例，同时保留原始图片信息的情形（如在网页中插入的图片，需要灵活地根据用户当前浏览页面的长宽比来调整插入图片的长宽比）。

例如，对于下面的图片，如何将其长度缩小为原来的一半同时保留其主要信息呢？

<p align="center">
    <img src="./figs/original.png" alt="original image" height="300">
</p>

最 naive 的想法是截取图像的半边，或者对图像做线性伸缩。其结果如下图所示。

<p align="center">
    <img src="./figs/compare.png" alt="resized image" height="300">
</p>
<p style="text-align: center; font-size: 12px; color: #666;">左图：将原始图像的长度线性伸缩为原来的一半的结果；右图：对原始图像截取左半侧的结果</p>

可以看到，我们确实达到了改变图像长宽比例的要求。但是原始图像的主要信息并没有得到充分保留：
- 对于左图，由于图像整体的长度被压缩，可以明显看到山丘和树木存在畸变；
- 对于右图，由于只截取了左半边，右半边的海角和礁石的信息没有得到保留

那么我们如何才能实现如下图所示的**既能改变长宽比例，又能尽可能多地保留图像信息**呢？

<p align="center">
    <img src="./figs/seamCarving.png" alt="seam carved image" height="300">
</p>
<p style="text-align: center; font-size: 12px; color: #666;">Seam Carving的结果：图像的主要信息得到了保留。</p>

## 实验要求

实现 2007 年 ToG 论文 [Seam Carving for Content-Aware Image Resizing](https://dl.acm.org/doi/10.1145/1276377.1276390) 中的接缝裁剪算法，用以改变图像的长宽比例。

实验报告中请展示如下内容：
- 简述算法的基本原理
- 展示图片裁剪的结果（缩小图片的长度、宽度）
- 对比实验：文中的方法与其他方法的对比（如截断、伸缩等）
- 对实验结果的必要说明

实现说明：
- 本次作业提供了 `MATLAB` , `Python` 和 `C++` 三套程序框架，可任选其一
- 本次实验不限制编程语言，但如果你不打算使用提供的框架，请自行搭建类似的图形界面
- 如果你有新解法或其他方面的创新，欢迎在报告中呈现

> 作为练习，我们鼓励大家完成论文中除接缝裁剪外的其他应用（如 Image Enlarging, Content Amplification, etc）

## MATLAB 框架

### 运行方式

在 MATLAB 中打开 `code_template/seam_carving.m`，直接运行即可。程序会启动一个图形界面，左侧显示原始图像，右侧显示裁剪结果。点击工具栏上的蓝色按钮即可触发 Seam Carving 裁剪（默认将图像宽度缩小 300 像素）。

### 需要完成的代码

请打开 `code_template/seam_carving.m`，补全 `seam_carve_image` 函数中标有 `TODO` 的部分：

| 步骤 | 说明 |
|------|------|
| 计算能量图 | 已提供 `costfunction`，利用 Laplacian 滤波器计算每个像素的能量值 |
| 寻找最优接缝 | 在能量图 `G` 上，使用动态规划找到一条从顶部到底部的最小能量路径（seam） |
| 移除接缝 | 将找到的 seam 从图像 `im` 中移除，使图像宽度减少 1 像素 |

框架中已提供的能量函数为：

$$e(x, y) = \sum_{c \in \{R,G,B\}} \left( \nabla^2 I_c(x, y) \right)^2$$

其中 $\nabla^2$ 为 Laplacian 算子，`costfunction` 使用 `[.5 1 .5; 1 -6 1; .5 1 .5]` 滤波核近似。每次迭代移除一条 seam，循环 `k` 次即可将图像宽度缩小 `k` 像素。

## Python 框架

我们也提供了一个 Python 实现框架，功能与 MATLAB 框架等价。

### 环境配置

推荐使用 [Miniforge](https://conda-forge.org/download/) 管理 Python 环境。

使用 conda 创建并激活环境：

```bash
conda create -n mm26 python=3.12
conda activate mm26
pip install numpy matplotlib scikit-image scipy
```

### 文件结构

```
code_template/
├── seam_carving.py      # Python 框架（需要补全）
└── seam_carving.m       # MATLAB 框架（需要补全）
```

### 运行方式

```bash
conda activate mm26
cd code_template
python seam_carving.py
```

运行后弹出 matplotlib 窗口，左侧显示原始图像，右侧显示裁剪结果。通过两个滑动条分别设置列（宽度）和行（高度）的缩放比例（0.5~2.0），点击 **Seam Carving** 按钮即可触发裁剪/放大。

### 需要完成的代码

请打开 `code_template/seam_carving.py`，补全标有 `TODO` 的 `seam_carve_image` 函数。该函数与 MATLAB 版本的接口完全一致：

| 函数 | 说明 |
|------|------|
| `seam_carve_image(im, sz)` | 输入原始图像 `im` 和目标尺寸 `sz = (target_h, target_w)`，返回调整后的图像 |

完成后，运行 `python seam_carving.py` 即可验证结果。欢迎进一步优化或实现更多功能。

## C++ 框架

我们同样提供了 C++ 实现框架，依赖 OpenCV 和标准库。

### 需要完成的代码

打开 `code_template_cpp/main.cpp`，找到 `TODO` 注释，实现以下函数：

```
seamCarveImage(img, target_rows, target_cols)
```

该函数将输入图像缩放到指定的目标尺寸。

### 编译

`code_template_cpp/` 目录下包含独立的 `CMakeLists.txt`，可直接在该目录下编译。

环境配置（安装 CMake、编译器、OpenCV）请参考 [BUILD_CPP.md](../../BUILD_CPP.md)。

```bash
# Linux / macOS（在 code_template_cpp/ 目录下执行）
mkdir build && cd build
cmake ..
make
```

```powershell
# Windows（在 code_template_cpp\ 目录下执行）
cmake -B build -DCMAKE_TOOLCHAIN_FILE=C:\vcpkg\scripts\buildsystems\vcpkg.cmake
cmake --build build --config Release
```

**推荐使用VS Code+ CMake Tools插件**：用 VS Code 打开 `code_template_cpp/` 文件夹，点击CMake Tools底部状态栏的 **Build** 即可。

### 运行方式

使用命令行编译时，可执行文件位于 `build/` 目录下；使用 VS Code CMake Tools 时通常也在 `build/` 下。

```bash
# 在 build/ 目录下运行，使用默认图片（../figs/original.png）
./op1_template

# 指定图片路径
./op1_template /path/to/image.png
```

> **Windows：**
> ```powershell
> .\op1_template.exe
> .\op1_template.exe C:\path\to\image.png
> ```

### GUI 说明

程序启动后会弹出一个窗口，左侧显示原图，右侧显示处理结果。

| 操作 | 说明 |
|------|------|
| 滑动 **Col %** 条 | 设置目标宽度（占原始宽度的百分比，10–200%）|
| 滑动 **Row %** 条 | 设置目标高度（占原始高度的百分比，10–200%）|
| 按 **Space** | 执行接缝裁剪，右侧显示结果 |
| 按 **s** | 将结果保存为 `result.png` |
| 按 **r** | 重置滑块与结果 |
| 按 **q / Esc** | 退出程序 |

处理进度会实时打印到终端。图像较大或调整幅度较大时，计算可能需要数秒，请耐心等待。
