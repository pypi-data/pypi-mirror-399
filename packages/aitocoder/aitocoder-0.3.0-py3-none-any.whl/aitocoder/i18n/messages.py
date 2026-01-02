"""
AitoCoder i18n Messages

This file contains all translatable messages for the AitoCoder REPL.
Messages are organized by category and support English (en) and Chinese (zh).

Message format:
    "key": {
        "en": "English text",
        "zh": "Chinese text",
    }

For messages with placeholders, use Python's str.format() syntax:
    "hello": {
        "en": "Hello, {name}!",
        "zh": "你好，{name}！",
    }
"""

MESSAGES = {
    # =========================================================================
    # Language Selection
    # =========================================================================
    "lang.selection_title": {
        "en": "Language Selection",
        "zh": "语言选择",
    },
    "lang.select_prompt": {
        "en": "Enter choice (1 or 2): ",
        "zh": "请输入选择 (1 或 2): ",
    },
    "lang.invalid_choice": {
        "en": "Invalid choice. Please enter 1 or 2.",
        "zh": "无效选择。请输入 1 或 2。",
    },
    "lang.default_english": {
        "en": "Defaulting to English.",
        "zh": "默认使用英语。",
    },

    # =========================================================================
    # REPL Entry - Welcome Panel (repl_entry.py)
    # =========================================================================
    "repl.welcome_to": {
        "en": "Welcome to",
        "zh": "欢迎使用",
    },
    "repl.cli_title": {
        "en": "AitoCoder CLI - REPL",
        "zh": "AitoCoder CLI - REPL",
    },
    "repl.visit_download": {
        "en": "Visit https://cli-download.aitocoder.com \n  for more info.",
        "zh": "请访问 https://cli-download.aitocoder.com \n  了解更多信息。",
    },
    "repl.visit_website": {
        "en": "Visit https://aitocoder.com \n  for sign-up, web platform and more.",
        "zh": "请访问 https://aitocoder.com \n  以注册账号、使用网页版等。",
    },
    "repl.ctrl_c_hint": {
        "en": "Ctrl+C to force quit a task.",
        "zh": "Ctrl+C 强制终止任务。",
    },
    "repl.ctrl_d_hint": {
        "en": "Ctrl+D to exit.",
        "zh": "Ctrl+D 退出。",
    },
    "repl.loading": {
        "en": "Loading... (First startup may take 30 seconds to a few minutes)",
        "zh": "正在加载中... （首次启动需要几十秒至数分钟）",
    },
    "repl.warn_no_git": {
        "en": "! Git is not installed. We recommend installing git for best experience.",
        "zh": "! 未安装 Git。建议安装 git 以获得最佳体验。",
    },
    "repl.warn_home_dir": {
        "en": "! Running in home directory. We recommend running in a project directory for best performance.",
        "zh": "! 正在主目录中运行。建议在项目目录中运行以获得最佳性能。",
    },

    # =========================================================================
    # REPL Entry - Login Flow (repl_entry.py)
    # =========================================================================
    "login.fetching_user_info": {
        "en": "Fetching user info...",
        "zh": "正在获取用户信息...",
    },
    "login.failed_fetch_user": {
        "en": "Failed to fetch user info",
        "zh": "获取用户信息失败",
    },
    "login.hello": {
        "en": "Hello, {username}!",
        "zh": "你好，{username}！",
    },
    "login.type_help": {
        "en": "Type /help to see available commands.",
        "zh": "输入 /help 查看可用命令。",
    },
    "login.username_prompt": {
        "en": "Username:",
        "zh": "用户名:",
    },
    "login.password_prompt": {
        "en": "Password:",
        "zh": "密码:",
    },
    "login.cancelled": {
        "en": "Login cancelled!",
        "zh": "登录已取消！",
    },
    "login.logging_in": {
        "en": "Logging in...",
        "zh": "正在登录...",
    },
    "login.failed": {
        "en": "Login failed",
        "zh": "登录失败",
    },
    "login.exit_hint": {
        "en": "Press Ctrl+C or Ctrl+D to exit",
        "zh": "按 Ctrl+C 或 Ctrl+D 退出",
    },
    "login.initializing_models": {
        "en": "Initializing models...",
        "zh": "正在初始化模型...",
    },
    "login.all_set": {
        "en": "You are all set!",
        "zh": "一切就绪！",
    },
    "login.model_init_failed": {
        "en": "Model initialization failed",
        "zh": "模型初始化失败",
    },

    # =========================================================================
    # REPL Entry - Errors (repl_entry.py)
    # =========================================================================
    "error.generic": {
        "en": "Error: {message}",
        "zh": "错误: {message}",
    },

    # =========================================================================
    # Chat Auto Coder - Help Menu (chat_auto_coder.py)
    # =========================================================================
    "help.official_doc": {
        "en": "Official Documentation (In Progress): https://cli-download.aitocoder.com",
        "zh": "官方文档（维护中）: https://cli-download.aitocoder.com",
    },
    "help.supported_commands": {
        "en": "Supported Commands:",
        "zh": "支持的命令:",
    },
    "help.start_building": {
        "en": "Enter your command after >>> and start building!",
        "zh": "在 >>> 后输入命令，开始构建！",
    },
    "help.change_model_hint": {
        "en": "Use /conf model:<model_name> to change the LLM model.",
        "zh": "使用 /conf model:<模型名> 来更换 LLM 模型。",
    },
    "help.commands": {
        "en": "Commands",
        "zh": "命令",
    },
    "help.description": {
        "en": "Description",
        "zh": "描述",
    },
    "help.auto_desc": {
        "en": "Intelligent auto-coding with AI agent",
        "zh": "使用 AI 智能体进行自动编程",
    },
    "help.auto_new_desc": {
        "en": "Start a new conversation",
        "zh": "开始新对话",
    },
    "help.auto_resume_desc": {
        "en": "Resume a previous conversation",
        "zh": "恢复之前的对话",
    },
    "help.auto_list_desc": {
        "en": "List all conversations",
        "zh": "列出所有对话",
    },
    "help.auto_command_desc": {
        "en": "Execute command from file",
        "zh": "从文件执行命令",
    },
    "help.commit_desc": {
        "en": "Commit changes with AI-generated message",
        "zh": "使用 AI 生成的消息提交更改",
    },
    "help.conf_desc": {
        "en": "Set configuration value",
        "zh": "设置配置值",
    },
    "help.shell_desc": {
        "en": "Execute shell command",
        "zh": "执行 shell 命令",
    },
    "help.shell_interactive_desc": {
        "en": "Enter interactive shell mode",
        "zh": "进入交互式 shell 模式",
    },
    "help.shell_single_command_desc": {
        "en": "Execute single shell command",
        "zh": "执行单个 shell 命令",
    },
    "help.add_files_desc": {
        "en": "Add files to context",
        "zh": "添加文件到上下文",
    },
    "help.remove_files_desc": {
        "en": "Remove files from context",
        "zh": "从上下文移除文件",
    },
    "help.chat_desc": {
        "en": "Chat with AI (no code generation)",
        "zh": "与 AI 对话（不生成代码）",
    },
    "help.coding_desc": {
        "en": "Generate code based on query",
        "zh": "根据查询生成代码",
    },
    "help.revert_desc": {
        "en": "Revert last code changes",
        "zh": "撤销上次代码更改",
    },
    "help.index_query_desc": {
        "en": "Query the code index",
        "zh": "查询代码索引",
    },
    "help.index_build_desc": {
        "en": "Build code index",
        "zh": "构建代码索引",
    },
    "help.list_files_desc": {
        "en": "List files in context",
        "zh": "列出上下文中的文件",
    },
    "help.help_desc": {
        "en": "Show this help message",
        "zh": "显示帮助信息",
    },
    "help.mode_desc": {
        "en": "View or set operation mode",
        "zh": "查看或设置操作模式",
    },
    "help.lib_desc": {
        "en": "Manage library packages",
        "zh": "管理库包",
    },
    "help.models_desc": {
        "en": "Manage AI models",
        "zh": "管理 AI 模型",
    },
    "help.plugins_desc": {
        "en": "Manage plugins",
        "zh": "管理插件",
    },
    "help.active_context_desc": {
        "en": "View active context",
        "zh": "查看活动上下文",
    },
    "help.exit_desc": {
        "en": "Exit the REPL",
        "zh": "退出 REPL",
    },

    # =========================================================================
    # Chat Auto Coder - Plugin Messages (chat_auto_coder.py)
    # =========================================================================
    "plugin.commands_title": {
        "en": "Plugin Commands:",
        "zh": "插件命令:",
    },
    "plugin.command_header": {
        "en": "Command",
        "zh": "命令",
    },
    "plugin.description_header": {
        "en": "Description",
        "zh": "描述",
    },
    "plugin.from": {
        "en": "from",
        "zh": "来自",
    },
    "plugin.from_unknown": {
        "en": "from unknown plugin",
        "zh": "来自未知插件",
    },
    "plugin.load_failed": {
        "en": "Failed to load builtin plugin {plugin_name}: {error}",
        "zh": "加载内置插件 {plugin_name} 失败: {error}",
    },
    "plugin.load_error": {
        "en": "Error loading builtin plugins: {error}",
        "zh": "加载内置插件时出错: {error}",
    },

    # =========================================================================
    # Chat Auto Coder - User Input Prompts (chat_auto_coder.py)
    # =========================================================================
    "input.please_enter_request": {
        "en": "Please enter your request.",
        "zh": "请输入您的请求。",
    },
    "input.please_enter_design_request": {
        "en": "Please enter your design request.",
        "zh": "请输入您的设计请求。",
    },
    "input.please_enter_query": {
        "en": "Please enter your query.",
        "zh": "请输入您的查询。",
    },
    "input.placeholder": {
        "en": "Type your command here...",
        "zh": "在此输入命令...",
    },
    "input.placeholder_next": {
        "en": "Enter your next command here...",
        "zh": "在此输入下一个命令...",
    },

    # =========================================================================
    # Chat Auto Coder - Mode Messages (chat_auto_coder.py)
    # =========================================================================
    "mode.switched_to_shell": {
        "en": "Switched to shell mode. Type commands directly, or /mode to switch back.",
        "zh": "已切换到 shell 模式。直接输入命令，或输入 /mode 切换回来。",
    },

    # =========================================================================
    # Chat Auto Coder - Task Status (chat_auto_coder.py)
    # =========================================================================
    "task.cancelled_by_user": {
        "en": "Operation cancelled by user",
        "zh": "用户取消了操作",
    },
    "task.cancelled": {
        "en": "Operation cancelled",
        "zh": "操作已取消",
    },
    "task.error_occurred": {
        "en": "An error occurred: {error_type} - {message}",
        "zh": "发生错误: {error_type} - {message}",
    },
    "task.callback_error": {
        "en": "Error in task completion callback: {error_type} - {message}",
        "zh": "任务完成回调出错: {error_type} - {message}",
    },
    "task.cleanup_error": {
        "en": "An error occurred while cleaning up: {error_type} - {message}",
        "zh": "清理时发生错误: {error_type} - {message}",
    },

    # =========================================================================
    # Chat Auto Coder - Goodbye (chat_auto_coder.py)
    # =========================================================================
    "repl.goodbye": {
        "en": "Goodbye!",
        "zh": "再见！",
    },

    # =========================================================================
    # Chat Auto Coder - Debug (chat_auto_coder.py)
    # =========================================================================
    "debug.result": {
        "en": "Debug result: {result}",
        "zh": "调试结果: {result}",
    },
    "debug.error": {
        "en": "Debug error: {error}",
        "zh": "调试错误: {error}",
    },

    # =========================================================================
    # Chat Auto Coder - Background Task (chat_auto_coder.py)
    # =========================================================================
    "background.task_error": {
        "en": "Background task error: {error}",
        "zh": "后台任务错误: {error}",
    },

    # =========================================================================
    # Auto Coder Runner - Project Config (auto_coder_runner.py)
    # =========================================================================
    "config.project_type_config": {
        "en": "Project Type Configuration",
        "zh": "项目类型配置",
    },
    "config.project_type_supports": {
        "en": "Supports file extensions or predefined types.",
        "zh": "支持文件扩展名或预定义类型。",
    },
    "config.language_suffixes": {
        "en": "Language suffixes: .py, .js, .ts, .java, .go, etc.",
        "zh": "语言后缀: .py, .js, .ts, .java, .go 等",
    },
    "config.predefined_types": {
        "en": "Predefined types: py, ts, java, go, etc.",
        "zh": "预定义类型: py, ts, java, go 等",
    },
    "config.mixed_projects": {
        "en": "For mixed projects, use comma-separated values.",
        "zh": "对于混合项目，使用逗号分隔的值。",
    },
    "config.examples": {
        "en": "Examples: .py,.js or py,ts or *",
        "zh": "示例: .py,.js 或 py,ts 或 *",
    },
    "config.default_type": {
        "en": "Default: * (all file types)",
        "zh": "默认: *（所有文件类型）",
    },
    "config.enter_project_type": {
        "en": "Enter project type: ",
        "zh": "输入项目类型: ",
    },
    "config.project_type_set": {
        "en": "Project type set to:",
        "zh": "项目类型已设置为:",
    },
    "config.using_default_type": {
        "en": "Using default project type.",
        "zh": "使用默认项目类型。",
    },
    "config.change_setting_later": {
        "en": "To change this setting later, use",
        "zh": "要稍后更改此设置，请使用",
    },
    "config.invalid_key": {
        "en": "Invalid configuration key: {key}",
        "zh": "无效的配置键: {key}",
    },
    "config.git_not_available": {
        "en": "Git module not available. Some git features will be disabled.",
        "zh": "Git 模块不可用。部分 git 功能将被禁用。",
    },

    # =========================================================================
    # Auto Coder Runner - Initialization (auto_coder_runner.py)
    # =========================================================================
    "init.complete": {
        "en": "Project initialization completed.",
        "zh": "项目初始化完成。",
    },
    "init.created_dir": {
        "en": "Created directory: {path}",
        "zh": "已创建目录: {path}",
    },

    # =========================================================================
    # Auto Coder Runner - Exclude Dirs (auto_coder_runner.py)
    # =========================================================================
    "exclude.added_dirs": {
        "en": "Added exclude dirs: {dirs}",
        "zh": "已添加排除目录: {dirs}",
    },
    "exclude.dirs_exist": {
        "en": "All specified dirs are already in the exclude list.",
        "zh": "所有指定目录都已在排除列表中。",
    },
    "exclude.added_files": {
        "en": "Added exclude files: {files}",
        "zh": "已添加排除文件: {files}",
    },
    "exclude.files_exist": {
        "en": "All specified files are already in the exclude list.",
        "zh": "所有指定文件都已在排除列表中。",
    },

    # =========================================================================
    # Terminal Runner - Task Status (terminal_runner.py)
    # =========================================================================
    "terminal.starting_task": {
        "en": "Starting Task",
        "zh": "开始任务",
    },
    "terminal.task_completion": {
        "en": "Task Completion",
        "zh": "任务完成",
    },
    "terminal.task_finished": {
        "en": "Task Finished",
        "zh": "任务结束",
    },
    "terminal.error": {
        "en": "Error",
        "zh": "错误",
    },
    "terminal.system_error": {
        "en": "System Error",
        "zh": "系统错误",
    },
    "terminal.fatal_error": {
        "en": "FATAL ERROR",
        "zh": "致命错误",
    },
    "terminal.success": {
        "en": "Success",
        "zh": "成功",
    },
    "terminal.failure": {
        "en": "Failure",
        "zh": "失败",
    },
    "terminal.status": {
        "en": "Status",
        "zh": "状态",
    },
    "terminal.message": {
        "en": "Message",
        "zh": "消息",
    },
    "terminal.content": {
        "en": "Content",
        "zh": "内容",
    },
    "terminal.suggested_command": {
        "en": "Suggested command:",
        "zh": "建议的命令:",
    },

    # =========================================================================
    # Terminal Runner - Conversation (terminal_runner.py)
    # =========================================================================
    "conversation.compacting": {
        "en": "Compacting conversation history...",
        "zh": "正在压缩对话历史...",
    },
    "conversation.compacting_title": {
        "en": "Memory Management",
        "zh": "内存管理",
    },
    "conversation.tokens": {
        "en": "conversation tokens: {used}",
        "zh": "对话 tokens: {used}",
    },
    "conversation.tokens_pruned": {
        "en": "conversation tokens: {used} -> {pruned} (round: {round})",
        "zh": "对话 tokens: {used} -> {pruned} (轮次: {round})",
    },

    # =========================================================================
    # Toolbar (chat_auto_coder.py)
    # =========================================================================
    "toolbar.project_dir": {
        "en": "Project Dir:",
        "zh": "项目目录:",
    },
    "toolbar.model": {
        "en": "Model:",
        "zh": "模型:",
    },
    "toolbar.async_tasks": {
        "en": "Async Tasks:",
        "zh": "异步任务:",
    },
    "toolbar.plugins": {
        "en": "Plugins:",
        "zh": "插件:",
    },

    # =========================================================================
    # Language Command
    # =========================================================================
    "lang.changed": {
        "en": "Language changed to: English",
        "zh": "语言已更改为: 简体中文",
    },
    "help.language_desc": {
        "en": "Change language settings",
        "zh": "更改语言设置",
    },
}
