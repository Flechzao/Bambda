# -*- coding: utf-8 -*-
# @Date     : 2024-12-09
# @File     : bambda.py
# @function : 核心代码，使用模板生成代码
from burp import IBurpExtender, ITab, IHttpListener
from javax.swing import JPanel, JTextField, JTextArea, JScrollPane, JCheckBox, JButton, BoxLayout, Box, BorderFactory, JLabel
from java.awt import GridBagLayout, GridBagConstraints, GridLayout, Insets, Dimension, FlowLayout
from constants import *

info = '''author:flechazo
Version:Bambda++ v1.1
description:通过选择HTTP方法、文件后缀、域名和关键字进行过滤，并自动生成相应的代码模板，相较于原生的“Convert to Bambda”功能，会更加贴近日常测试。
'''
print(info)

# 定义HTTP方法和常见文件后缀
HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH", "TRACE", "CONNECT"]
COMMON_SUFFIXES = [".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".html", ".svg"]

class BurpExtender(IBurpExtender, ITab, IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        """
        注册扩展回调方法
        """
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("Bambda++")

        # 初始化用于存储复选框的列表
        self.http_method_checkboxes = []
        self.suffix_checkboxes = []

        self.create_ui()
        callbacks.addSuiteTab(self)
        callbacks.registerHttpListener(self)
        #callbacks.registerContextMenuFactory(self)

    def create_ui(self):
        """
        创建用户界面
        """
        self.panel = JPanel()
        self.panel.setLayout(BoxLayout(self.panel, BoxLayout.Y_AXIS))

        # 创建 HTTP 方法和文件后缀过滤部分在同一行展示
        top_panel = JPanel()
        top_layout = GridBagLayout()
        top_panel.setLayout(top_layout)
        constraints = GridBagConstraints()
        constraints.fill = GridBagConstraints.BOTH
        constraints.insets = Insets(5, 5, 5, 5)

        # HTTP 方法面板
        filter_method_panel = self.create_http_method_filter_panel()
        constraints.gridx = 0
        constraints.gridy = 0
        constraints.weightx = 3
        top_panel.add(filter_method_panel, constraints)

        # 文件后缀面板
        filter_suffix_panel = self.create_suffix_filter_panel()
        constraints.gridx = 1
        constraints.gridy = 0
        constraints.weightx = 4
        top_panel.add(filter_suffix_panel, constraints)

        # 文本面板
        note_panel = self.create_note_panel()
        constraints.gridx = 2
        constraints.gridy = 0
        constraints.weightx = 2
        top_panel.add(note_panel, constraints)

        # 添加顶层面板到主面板
        self.panel.add(top_panel)

        # 域名过滤部分
        domain_panel = self.create_text_area_panel(
            "domain", decode_text(STRINGS['Exclude Domains']),
            JTextArea(3, 50),
            "hcfy.*,detectportal.firefox.com,http://www.google-analytics.com"
            "firefox.settings.services.mozilla.com,incoming.telemetry.mozilla.org,"
            
        )
        self.panel.add(domain_panel)

        # 仅查看关键字过滤部分
        keyword_panel = self.create_text_area_panel("keywords", decode_text(STRINGS['keywords']),
                                                    JTextArea(3, 50),
                                                    "login,com"
                                                    )
        self.panel.add(keyword_panel)

        # 排除关键字过滤部分
        exclude_keyword_panel = self.create_text_area_panel("exclude_keywords", decode_text(STRINGS['Exclude keywords']),
                                                            JTextArea(3, 50),
                                                            "debug,interna"
                                                            )
        self.panel.add(exclude_keyword_panel)

        # 生成代码按钮和输出区域
        generate_button_panel = JPanel()
        generate_button_panel.setLayout(BoxLayout(generate_button_panel, BoxLayout.X_AXIS))
        self.generate_button = JButton(decode_text(STRINGS['Generate Code']), actionPerformed=self.generate_code)
        generate_button_panel.add(self.generate_button)
        self.panel.add(generate_button_panel)

        self.output_area = JTextArea(15, 50)
        self.output_area.setEditable(False)
        self.output_area.setPreferredSize(Dimension(500, 100))  # 调整输出区域大小
        self.panel.add(JScrollPane(self.output_area))

    def create_http_method_filter_panel(self):
        """
        创建包含所有HTTP方法复选框的面板。
        """
        panel = JPanel()
        panel.setBorder(BorderFactory.createTitledBorder("HTTP Method"))
        panel.setLayout(GridBagLayout())
        panel.setPreferredSize(Dimension(300, 100))  # 调整面板大小

        top_checkbox = JCheckBox(decode_text(STRINGS['Exclude HTTP Methods']))
        top_constraints = GridBagConstraints()
        top_constraints.gridx = 0
        top_constraints.gridy = 0
        top_constraints.anchor = GridBagConstraints.WEST
        top_constraints.insets = Insets(5, 5, 5, 5)
        panel.add(top_checkbox, top_constraints)
        self.filter_method_checkbox = top_checkbox

        methods_panel = JPanel()
        methods_panel.setLayout(GridLayout(0, 5))  # 设置每行5个复选框
        methods_panel.setPreferredSize(Dimension(300, 100))  # 调整面板大小

        for method in HTTP_METHODS:
            checkbox = JCheckBox(method)
            if method not in ["GET", "POST", "PUT", "DELETE"]:
                checkbox.setSelected(True)
            methods_panel.add(checkbox)
            self.http_method_checkboxes.append(checkbox)

        methods_constraints = GridBagConstraints()
        methods_constraints.gridx = 0
        methods_constraints.gridy = 1
        methods_constraints.gridwidth = 3
        methods_constraints.fill = GridBagConstraints.HORIZONTAL
        methods_constraints.insets = Insets(10, 10, 10, 10)
        panel.add(methods_panel, methods_constraints)

        return panel

    def create_suffix_filter_panel(self):
        """
        创建包含常见文件后缀复选框以及输入字段的面板。
        """
        panel = JPanel()
        panel.setBorder(BorderFactory.createTitledBorder("File Suffixes"))
        panel.setLayout(GridBagLayout())
        panel.setPreferredSize(Dimension(300, 200))  # 调整File Suffixes 面板大小

        top_checkbox = JCheckBox(decode_text(STRINGS['Exclude File Suffixes']))
        top_constraints = GridBagConstraints()
        top_constraints.gridx = 0
        top_constraints.gridy = 0
        top_constraints.anchor = GridBagConstraints.WEST #
        top_constraints.insets = Insets(5, 5, 5, 5)
        panel.add(top_checkbox, top_constraints)
        self.filter_suffix_checkbox = top_checkbox

        suffixes_panel = JPanel()
        suffixes_panel.setLayout(GridLayout(0, 5))  # 设置为每行5个复选框
        suffixes_panel.setPreferredSize(Dimension(300, 200))  #

        for suffix in COMMON_SUFFIXES:
            checkbox = JCheckBox(suffix)
            suffixes_panel.add(checkbox)
            self.suffix_checkboxes.append(checkbox)

        suffixes_constraints = GridBagConstraints()
        suffixes_constraints.gridx = 0
        suffixes_constraints.gridy = 1
        suffixes_constraints.gridwidth = 4
        suffixes_constraints.fill = GridBagConstraints.HORIZONTAL
        suffixes_constraints.insets = Insets(5, 5, 5, 5)
        panel.add(suffixes_panel, suffixes_constraints)

        self.suffix_input_field = JTextField(".ts,.jsx")
        input_field_constraints = GridBagConstraints()
        input_field_constraints.gridx = 0
        input_field_constraints.gridy = 2
        input_field_constraints.gridwidth = 4
        input_field_constraints.fill = GridBagConstraints.HORIZONTAL
        input_field_constraints.insets = Insets(5, 5, 5, 5)
        panel.add(self.suffix_input_field, input_field_constraints)

        return panel

    def create_note_panel(self):
        """
        创建使用方法、作者说明的面板。
        """
        panel = JPanel()
        panel.setLayout(BoxLayout(panel, BoxLayout.Y_AXIS))
        panel.setBorder(BorderFactory.createTitledBorder("Note"))

        #note_area = JTextArea(decode_text(STRINGS['Author']) + "\n" + decode_text(STRINGS['Usage']))
        note_area = JTextArea("\n" + "\n" + "author:flechazo"+ "\n" + "Version:Bambda++ v1.0")

        note_area.setLineWrap(True)
        note_area.setWrapStyleWord(True)
        note_area.setEditable(False)
        note_area.setOpaque(False)

        # 设置固定的大小
        panel.setPreferredSize(Dimension(150, 180))
        panel.setMinimumSize(Dimension(150, 180))
        panel.setMaximumSize(Dimension(150, 180))

        panel.add(note_area)

        return panel

    def create_text_area_panel(self, title, checkbox_label, text_area, default_text=""):
        """
        创建包含复选框和滚动文本区域的面板。
        """
        panel = JPanel()
        panel.setBorder(BorderFactory.createTitledBorder(title))
        panel.setLayout(BoxLayout(panel, BoxLayout.Y_AXIS))

        # 左对齐复选框
        checkbox_panel = JPanel()
        checkbox_panel.setLayout(FlowLayout(FlowLayout.LEFT))
        checkbox = JCheckBox(checkbox_label)
        checkbox_panel.add(checkbox)
        panel.add(checkbox_panel)

        if isinstance(text_area, JTextArea):
            text_area.setText(default_text)
            text_area.setLineWrap(True)
            text_area.setWrapStyleWord(True)  # 按单词换行
            #text_area.setPreferredSize(Dimension(500, 100))# 调整文本区域大小
            text_area.setRows(4)  # 设置文本框高度（行数）
            text_area.setColumns(50)  # 可以根据需要设置列数

        scroll_pane = JScrollPane(text_area)
        panel.add(scroll_pane)

        if title == "domain":
            self.filter_domain_checkbox = checkbox
            self.domain_exclude_field = text_area
        elif title == "keywords":
            self.filter_keyword_checkbox = checkbox
            self.keywords_field = text_area
        elif title == "exclude_keywords":
            self.filter_exclude_keyword_checkbox = checkbox
            self.exclude_keywords_field = text_area

        return panel

    def generate_code(self, event):
        """
        根据用户选择的过滤条件生成代码并显示在输出区域。
        """
        methods = [cb.getText() for cb in self.http_method_checkboxes if cb.isSelected()]
        domain_excludes = self.domain_exclude_field.getText().split(',')
        keywords = self.keywords_field.getText().split(',')
        exclude_keywords = self.exclude_keywords_field.getText().split(',')  # 获取排除关键字
        suffixes = [cb.getText() for cb in self.suffix_checkboxes if
                    cb.isSelected()] + self.suffix_input_field.getText().split(',')

        code_lines = []

        if methods:
            code_lines.append(
                'String[] methodExclude = {{{}}};\n'.format(", ".join('"{}"'.format(m.strip()) for m in methods)))
            code_lines.append("String method = requestResponse.request().method();\n")

        if self.filter_domain_checkbox.isSelected():
            code_lines.append('String[] domainExclude = {{{}}};\n'.format(
                ", ".join('"{}"'.format(d.strip()) for d in domain_excludes)))
            code_lines.append("String host = requestResponse.request().httpService().host();\n")

        if self.filter_keyword_checkbox.isSelected():
            code_lines.append(
                'String[] keywords = {{{}}};\n'.format(", ".join('"{}"'.format(k.strip()) for k in keywords)))
            code_lines.append(
                "boolean containsAnyKeyword = Arrays.stream(keywords).anyMatch(keyword -> requestResponse.contains(keyword, false));\n")

        if self.filter_exclude_keyword_checkbox.isSelected():
            code_lines.append(
                'String[] excludeKeywords = {{{}}};\n'.format(", ".join('"{}"'.format(ek.strip()) for ek in exclude_keywords)))
            code_lines.append(
                "boolean containsExcludeKeyword = Arrays.stream(excludeKeywords).anyMatch(keyword -> requestResponse.contains(keyword, false));\n")

        if self.filter_suffix_checkbox.isSelected():
            code_lines.append(
                'String[] pathExclude = {{{}}};\n'.format(", ".join('"{}"'.format(s.strip()) for s in suffixes)))
            code_lines.append("String path = requestResponse.request().pathWithoutQuery().toLowerCase();\n")
            code_lines.append(
                "boolean isExcludedSuffix = Arrays.stream(pathExclude).anyMatch(it -> path.endsWith(it));\n")

        conditions = []
        if methods:
            conditions.append("Arrays.stream(methodExclude).noneMatch(it -> method.contains(it))")
        if self.filter_domain_checkbox.isSelected():
            conditions.append("Arrays.stream(domainExclude).noneMatch(it -> host.contains(it))")
        if self.filter_keyword_checkbox.isSelected():
            conditions.append("containsAnyKeyword")
        if self.filter_exclude_keyword_checkbox.isSelected():  # 新增部分
            conditions.append("!containsExcludeKeyword")
        if self.filter_suffix_checkbox.isSelected():
            conditions.append("!isExcludedSuffix")

        if conditions:
            code_lines.append("return " + " && ".join(conditions) + ";\n")

        self.output_area.setText(''.join(code_lines))

    # 保障原始过滤模式下能正常过滤OPTIONS请求
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        if messageIsRequest or toolFlag != 4:
            return
        requestBytes = messageInfo.getRequest()
        requestInfo = self._helpers.analyzeRequest(requestBytes)
        if requestInfo.getMethod() != "OPTIONS":
            return
        responseBytes = messageInfo.getResponse()
        responseInfo = self._helpers.analyzeResponse(responseBytes)
        responseHeaders = responseInfo.getHeaders()
        responseHeaders = [header for header in responseHeaders if not header.startswith("Content-Type: ")]
        responseHeaders.append("Content-Type: text/css; charset=UTF-8")
        responseBodyBytes = b"/* Injected by 'Filter OPTIONS Method' */"
        responseModified = self._helpers.buildHttpMessage(responseHeaders, responseBodyBytes)
        messageInfo.setResponse(responseModified)

    def getTabCaption(self):
        """
        获取选项卡的标题。
        """
        return "Bambda++"

    def getUiComponent(self):
        """
        获取 UI 组件。
        """
        return self.panel
