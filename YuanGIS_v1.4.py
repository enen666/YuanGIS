# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 原作者的版权声明
# ----------------------------------------------------------------------
# Copyright (c) 2024 JesseBean. MIT License.
# Edited on 2024/10/31
# @author: Jiaxing Dou (jiaxingdou@mail.bnu.edu.cn)
# @coauthor: Yiran Tan (202311079938@mail.bnu.edu.cn)
# ----------------------------------------------------------------------
# 本项目作者的版权声明
# ----------------------------------------------------------------------
# Copyright (c) 2025 Zhuojiang Zou. MIT License.
# Edited on 2025/04/03
# @author: Zhuojiang Zou (202311079947@mail.bnu.edu.cn)
# ----------------------------------------------------------------------


import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QInputDialog,
    QDialog,
    QTextEdit,
    QPushButton,
    QTableView,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QAbstractTableModel  # 添加这一行以导入 Qt 模块
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
import geopandas as gpd
from ui import Ui_MainWindow  # 导入ui界面


class PandasModel(QAbstractTableModel):
    """
    将DataFrame的内容填充至表格
    """

    def __init__(self, data):
        super(PandasModel, self).__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 设置包括主窗口在内的所有窗口的标题和图标
        self.setWindowTitle("Yuan GIS - v1.4")  # 👈 设置窗口标题
        self.setWindowIcon(QIcon(r"icons\YuanGIS.png"))

        # 初始化地理数据存储
        self.gdf = None

        # 初始化 Matplotlib 组件
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)

        # 确保 plotWidget 在 Qt Designer 中已设置布局（如垂直布局）
        if not self.plotWidget.layout():
            layout = QVBoxLayout()
            self.plotWidget.setLayout(layout)
        self.plotWidget.layout().addWidget(self.canvas)

        # 初始化坐标轴
        self.ax = self.figure.add_subplot(111)
        self.ax.set_axis_off()

        # 创建并添加自定义导航工具栏
        self.toolbar = CustomNavigationToolbar(self.canvas, self)
        self.addToolBar(Qt.BottomToolBarArea, self.toolbar)  # 将工具栏放在底部

        # 获取默认状态栏中的 QLabel
        self.status_label = QLabel("就绪", alignment=Qt.AlignCenter)
        self.statusBar.addWidget(self.status_label)

        # 更新初始状态栏消息
        self.update_status_message("就绪")

        # 绑定菜单动作
        self.actionImport.triggered.connect(self.import_shp)
        self.actionExit.triggered.connect(self.close)
        self.actionGetProjectionInfo.triggered.connect(self.show_projection_info)
        self.actionConvertProjection.triggered.connect(self.switch_projection)
        self.actionClearData.triggered.connect(self.clear_data)
        self.actionShowAttributeTable.triggered.connect(self.show_attribute_table)
        self.actionExportAsPng.triggered.connect(self.export_as_png)
        self.actionExportAsShp.triggered.connect(self.export_as_shp)
        self.actionExportAsCSV.triggered.connect(self.export_as_csv)
        self.actionUsageInstructions.triggered.connect(self.show_usage_instructions)
        self.actionAbout.triggered.connect(self.show_about_dialog)

    def update_status_message(self, message):
        """更新状态栏消息"""
        self.status_label.setText(message)

    def import_shp(self):
        """导入并可视化 SHP 文件"""
        try:
            filepath, _ = QFileDialog.getOpenFileName(
                self, "选择SHP文件", "", "Shapefiles (*.shp)"
            )
            if not filepath:
                self.update_status_message("操作已取消")
                return

            # 加载数据
            self.gdf = gpd.read_file(filepath)
            self.update_status_message(f"已加载: {os.path.basename(filepath)}")

            # 可视化
            self.plot_geodata()

        except Exception as e:
            self.update_status_message(f"错误: {str(e)}")
            self.gdf = None

    def plot_geodata(self):
        """执行可视化操作"""
        if self.gdf is None:
            return

        try:
            self.figure.clear() # 清空Matplotlib画布，移除之前的图形元素
            self.ax = self.figure.add_subplot(111) # 创建新的坐标系，111表示单视图布局
            self.gdf.plot(ax=self.ax, edgecolor="k", linewidth=0.5) # 调用geopandas的矢量绘图方法，设置黑色边界线（edgecolor="k"）和0.5线宽
            self.ax.autoscale() # 自动调整坐标轴范围以适应地理数据空间范围
            self.canvas.draw() # 强制重绘Qt画布组件，实现可视化更新
        except Exception as e:
            self.update_status_message(f"渲染错误: {str(e)}")

    # 以下代码源自 BanyanGIS 项目（MIT协议）（Zhuojiang Zou，2025/04/03）
    # 原项目地址：https://github.com/BeanJ/BanyanGIS
    def show_projection_info(self):
        """Displays the projection information."""
        try:
            projection_info = (
                self.gdf.crs.to_string() if self.gdf.crs else "Undefined projection"
            )

            # Create a dialog to display the projection information
            # Use the main window as the parent
            dialog = QDialog(self)
            dialog.setWindowTitle("Projection Info")

            # Create a text edit widget to display the information
            text_edit = QTextEdit(dialog)
            # Set the projection information
            text_edit.setPlainText(projection_info)
            text_edit.setReadOnly(True)  # Make it read-only

            # Create a layout for the dialog
            layout = QVBoxLayout(dialog)
            layout.addWidget(text_edit)

            # Add a copy button
            copy_button = QPushButton("Copy", dialog)
            copy_button.clicked.connect(
                lambda: self.copy_to_clipboard(text_edit.toPlainText())
            )  # Connect to copy function
            layout.addWidget(copy_button)

            # Add a close button
            close_button = QPushButton("Close", dialog)
            # Close the dialog when button is clicked
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)

            dialog.setLayout(layout)
            dialog.resize(600, 400)  # Set the initial size of the dialog

            dialog.exec_()  # Show the dialog
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to get projection info: {e}",
            )

    # 以下代码源自 BanyanGIS 项目（MIT协议）（Zhuojiang Zou，2025/04/03）
    # 原项目地址：https://github.com/BeanJ/BanyanGIS
    def copy_to_clipboard(self, text):
        """Copy the text to clipboard."""
        clipboard = QApplication.clipboard()  # Get the clipboard
        clipboard.setText(text)  # Copy the text

    def switch_projection(self):
        """转换投影"""
        try:
            epsg_code, ok = QInputDialog.getText(self, "切换投影", "请输入EPSG代码:")
            if not ok or not epsg_code.isdigit():
                QMessageBox.warning(self, "警告", "无效的EPSG代码。")
                return

            epsg_code = int(epsg_code)
            self.gdf = self.gdf.to_crs(epsg=f"{epsg_code}")
            self.update_status_message(f"投影已切换为EPSG:{epsg_code}")
            self.plot_geodata()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"切换投影失败: {e}")

    def clear_data(self):
        """清除数据"""
        self.gdf = None
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_axis_off()
        self.canvas.draw()
        self.update_status_message("数据已清除")

    def show_attribute_table(self):
        """展示已加载数据的属性表"""
        try:
            if self.gdf is None:
                QMessageBox.warning(self, "警告", "尚未加载任何数据集。")
                return

            # 创建一个对话框来显示属性表
            dialog = QDialog(self)
            dialog.setWindowTitle("属性表")

            # 创建一个表格视图小部件来显示属性表
            table_view = QTableView(dialog)
            model = PandasModel(self.gdf)
            table_view.setModel(model)

            # 为对话框创建一个布局
            layout = QVBoxLayout(dialog)
            layout.addWidget(table_view)

            # 添加一个关闭按钮
            close_button = QPushButton("关闭", dialog)
            # 点击按钮时关闭对话框
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)

            dialog.setLayout(layout)
            dialog.resize(800, 600)  # 设置对话框的初始大小

            dialog.exec_()  # 显示对话框
        except Exception as e:
            QMessageBox.critical(
                self,
                "错误",
                f"显示属性表失败: {e}",
            )

    def export_as_png(self):
        """将现有图形导出为png"""
        try:
            if self.gdf is None:
                QMessageBox.warning(self, "警告", "尚未加载任何数据集。")
                return

            filepath, _ = QFileDialog.getSaveFileName(
                self, "保存PNG文件", "", "PNG Files (*.png)"
            )
            if not filepath:
                self.update_status_message("操作已取消")
                return

            # 将图像保存为PNG文件
            self.figure.savefig(filepath, dpi=300)
            self.update_status_message(f"图像已保存为: {os.path.basename(filepath)}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "错误",
                f"导出PNG文件失败: {e}",
            )

    def export_as_shp(self):
        """将现有地理数据导出为shp"""
        try:
            if self.gdf is None:
                QMessageBox.warning(self, "警告", "尚未加载任何数据集。")
                return

            filepath, _ = QFileDialog.getSaveFileName(
                self, "保存SHP文件", "", "Shapefiles (*.shp)"
            )
            if not filepath:
                self.update_status_message("操作已取消")
                return

            # 确保文件路径以.shp结尾
            if not filepath.endswith(".shp"):
                filepath += ".shp"

            # 将GeoDataFrame保存为shapefile
            self.gdf.to_file(filepath)
            self.update_status_message(f"SHP文件已保存为: {os.path.basename(filepath)}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "错误",
                f"导出SHP文件失败: {e}",
            )

    def export_as_csv(self):
        """将现有地理数据的属性表导出为csv"""
        try:
            if self.gdf is None:
                QMessageBox.warning(self, "警告", "尚未加载任何数据集。")
                return

            filepath, _ = QFileDialog.getSaveFileName(
                self, "保存CSV文件", "", "CSV Files (*.csv)"
            )
            if not filepath:
                self.update_status_message("操作已取消")
                return

            # 确保文件路径以.csv结尾
            if not filepath.endswith(".csv"):
                filepath += ".csv"

            # 将GeoDataFrame的属性保存为CSV文件
            self.gdf.to_csv(filepath, index=False)
            self.update_status_message(f"CSV文件已保存为: {os.path.basename(filepath)}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "错误",
                f"导出CSV文件失败: {e}",
            )

    def show_about_dialog(self):
        """显示关于对话框"""
        about_text = (
            "<h2>YuanGIS</h2>"
            "<p>版本: 1.4 | 开源协议: MIT</p>"
            "<p>项目地址：<a href='https://github.com/enen666/YuanGIS'>github.com/enen666/YuanGIS</a></p>"
            "<p>项目描述：一个轻量级教学用GIS平台，支持空间数据管理与可视化分析。</p>"
            "<p>开发者：邹卓江</p>"
            "<p>学术指导：屈永华 教授</p>"
            "<h3>开源致谢</h3>"
            "<p>本软件基于开源项目 BanyanGIS 二次开发，特别感谢其开发者窦家兴、谭依然同学提供的核心技术支持。</p>"
            "<p>原项目地址：<a href='https://github.com/BeanJ/BanyanGIS'>github.com/BeanJ/BanyanGIS</a></p>"
        )
        QMessageBox.about(self, "关于YuanGIS", about_text)

    def show_usage_instructions(self):
        """显示使用说明"""
        instructions_text = (
            "<h2>使用说明</h2>"
            "<p><strong>导入数据:</strong> 使用 '文件 -> 导入' 菜单项来加载一个Shapefile (.shp).</p>"
            "<p><strong>查看投影信息:</strong> 使用 '操作 -> 查看投影信息' 来查看当前数据集的投影.</p>"
            "<p><strong>切换投影:</strong> 使用 '操作 -> 切换投影' 来更改数据集的投影.</p>"
            "<p><strong>显示属性表:</strong> 使用 '操作 -> 显示属性表' 来查看数据集的属性表.</p>"
            "<p><strong>清空数据:</strong> 使用 '操作 -> 清空数据' 来清除当前加载的数据.</p>"
            "<p><strong>导出数据:</strong> 使用 '导出' 子菜单来将数据导出为不同的格式 (PNG, SHP, CSV).</p>"
        )
        QMessageBox.information(self, "使用说明", instructions_text)


# 以下代码引用自 BanyanGIS 项目（MIT协议），并针对本项目进行修改（Zhuojiang Zou，2025/04/03）
# 原项目地址：https://github.com/BeanJ/BanyanGIS
class CustomNavigationToolbar(NavigationToolbar):
    '''工具栏'''
    toolitems = [t for t in NavigationToolbar.toolitems if t[0] != "Save"]

    def __init__(self, canvas, parent, coordinates=True):
        super().__init__(canvas, parent, coordinates)
        self._icon_paths = {
            "Home": r"icons\home.png",
            "Back": r"icons\pfanhui.png",
            "Forward": r"icons\pforward.png",
            "Pan": r"icons\pan.png",
            "Zoom": r"icons\zoom.png",
            "Subplots": r"icons\edit-border.png",
            "Customize": r"icons\edit-text.png",
        }
        self._update_icons()

    def _update_icons(self):
        for action in self.actions():
            if action.text() in self._icon_paths:
                icon_path = self._icon_paths[action.text()]
                action.setIcon(QIcon(icon_path))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
