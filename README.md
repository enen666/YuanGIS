# YuanGIS 

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## 项目简介
**YuanGIS** 是一款面向地理信息科学（GIS）教学的原型系统，基于开源项目 [BanyanGIS](https://github.com/BeanJ/BanyanGIS) 二次开发，提供基础地理信息系统功能的教学演示与实验支持。核心功能包括：  
✅ Shapefile 数据导入与解析  
✅ 交互式地图可视化  
✅ 地理坐标系元数据管理  
✅ 属性表分析及数据导出  

---

## 功能特性
### 数据管理
- **Shapefile 导入**  
  支持标准 Shapefile 格式（`.shp`, `.shx`, `.dbf`）的加载与解析，兼容点、线、面矢量数据类型。
- **多源数据导出**  
  支持将地图导出为 `PNG` 图像或 `Shapefile`，属性表可导出为 `CSV` 格式。

### 可视化与分析
- **交互式地图渲染**  
  提供缩放、平移、视图切换等基础交互操作。
- **坐标系管理**  
  自动识别数据投影信息（如 EPSG 编码），支持常见坐标系转换（需预设转换参数）。
- **属性表查看**  
  以表格形式展示要素属性。

---

## 代码构成与协议
### 代码引用声明
- **引用模块**  
  - 自定义工具栏（CustomNavigationToolbar类） 
  - 获取投影信息功能（show_projection_info、copy_to_clipboard两个函数）  
  - 引用代码占比：14%（基于代码行数统计）
- **原创模块**  
  - 数据导入/导出功能 
  - 属性表展示功能
  - 界面设计与实现

### 开源协议
- 本项目遵循 MIT 许可证，详情请查看 [LICENSE](./LICENSE.txt) 文件。  

---

## 联系信息
如需技术协助或功能建议，请通过以下方式联系：
- **邮箱**：202311079947@mail.bnu.edu.cn
- **GitHub**： [YuanGIS Repository](https://github.com/enen666/YuanGIS)
