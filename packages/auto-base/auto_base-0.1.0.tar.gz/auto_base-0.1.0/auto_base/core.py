# 导入 autogen 库
import autogen

# 尝试导入 ag2，失败时设为 None
try:
    import ag2
    AG2_AVAILABLE = True
except ImportError:
    ag2 = None
    AG2_AVAILABLE = False

class AutoBase:
    """A thin wrapper around ag2 (optional) and autogen libraries, providing simplified interface for easy usage"""
    
    def __init__(self, *args, **kwargs):
        """Initialize the wrapper"""
        self.ag2 = ag2
        self.autogen = autogen
        self.ag2_available = AG2_AVAILABLE
    
    def __getattr__(self, name):
        """Forward attribute access to the underlying autogen instance by default"""
        return getattr(self.autogen, name)
    
    # ---------------------------
    # AG2 相关方法
    # ---------------------------
    def get_ag2_instance(self):
        """Get the raw ag2 instance"""
        return self.ag2
    
    # ---------------------------
    # Autogen 代理创建方法
    # ---------------------------
    def create_assistant_agent(
        self, 
        name="assistant", 
        system_message=None, 
        llm_config=None
    ):
        """
        Create an AssistantAgent instance with simplified parameters
        
        Args:
            name: Name of the agent
            system_message: System message for the agent
            llm_config: LLM configuration
        
        Returns:
            autogen.AssistantAgent instance
        """
        return self.autogen.AssistantAgent(
            name=name,
            system_message=system_message,
            llm_config=llm_config
        )
    
    def create_user_proxy_agent(
        self, 
        name="user_proxy", 
        code_execution_config=None,
        human_input_mode="NEVER"
    ):
        """
        Create a UserProxyAgent instance with simplified parameters
        
        Args:
            name: Name of the agent
            code_execution_config: Code execution configuration
            human_input_mode: Human input mode ("NEVER", "TERMINAL", "ALWAYS")
        
        Returns:
            autogen.UserProxyAgent instance
        """
        return self.autogen.UserProxyAgent(
            name=name,
            code_execution_config=code_execution_config,
            human_input_mode=human_input_mode
        )
    
    def create_group_chat(
        self, 
        agents, 
        messages=None, 
        max_round=10,
        speaker_selection_method="auto"
    ):
        """
        Create a GroupChat instance with simplified parameters
        
        Args:
            agents: List of agents
            messages: Initial messages
            max_round: Maximum number of rounds
            speaker_selection_method: Speaker selection method
        
        Returns:
            autogen.GroupChat instance
        """
        return self.autogen.GroupChat(
            agents=agents,
            messages=messages or [],
            max_round=max_round,
            speaker_selection_method=speaker_selection_method
        )
    
    def create_group_chat_manager(
        self, 
        groupchat, 
        llm_config=None
    ):
        """
        Create a GroupChatManager instance with simplified parameters
        
        Args:
            groupchat: GroupChat instance
            llm_config: LLM configuration
        
        Returns:
            autogen.GroupChatManager instance
        """
        return self.autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config=llm_config
        )
    
    # ---------------------------
    # 配置相关方法
    # ---------------------------
    def config_list_from_dotenv(self, dotenv_file_path=None):
        """
        Load configuration list from .env file
        
        Args:
            dotenv_file_path: Path to .env file
        
        Returns:
            List of configurations
        """
        return self.autogen.config_list_from_dotenv(
            dotenv_file_path=dotenv_file_path
        )
    
    def config_list_from_json(self, file_path, filter_dict=None):
        """
        Load configuration list from JSON file
        
        Args:
            file_path: Path to JSON file
            filter_dict: Filter dictionary
        
        Returns:
            List of configurations
        """
        return self.autogen.config_list_from_json(
            file_path=file_path,
            filter_dict=filter_dict
        )
    
    def config_list_gpt4_gpt35(self):
        """
        Get configuration list for GPT-4 and GPT-3.5 models
        
        Returns:
            List of configurations
        """
        return self.autogen.config_list_gpt4_gpt35()
    
    # ---------------------------
    # 工具注册方法
    # ---------------------------
    def register_function(
        self, 
        func, 
        callable_agent=None,
        name=None,
        description=None
    ):
        """
        Register a function for agents to call
        
        Args:
            func: Function to register
            callable_agent: Agent that can call the function
            name: Name of the function
            description: Description of the function
        
        Returns:
            None
        """
        return self.autogen.register_function(
            func=func,
            callable_agent=callable_agent,
            name=name,
            description=description
        )
    
    # ---------------------------
    # 聊天启动方法
    # ---------------------------
    def initiate_chat(
        self, 
        sender, 
        receiver, 
        message, 
        **kwargs
    ):
        """
        Initiate a chat between two agents
        
        Args:
            sender: Sender agent
            receiver: Receiver agent
            message: Initial message
            **kwargs: Additional arguments
        
        Returns:
            Chat result
        """
        return sender.initiate_chat(
            receiver=receiver,
            message=message,
            **kwargs
        )
    
    def initiate_group_chat(
        self, 
        group_chat_manager, 
        message, 
        **kwargs
    ):
        """
        Initiate a group chat
        
        Args:
            group_chat_manager: Group chat manager
            message: Initial message
            **kwargs: Additional arguments
        
        Returns:
            Chat result
        """
        return group_chat_manager.initiate_chat(
            message=message,
            **kwargs
        )
    
    # ---------------------------
    # 工具函数
    # ---------------------------
    def gather_usage_summary(self, chat_results):
        """
        Gather usage summary from chat results
        
        Args:
            chat_results: List of chat results
        
        Returns:
            Usage summary
        """
        return self.autogen.gather_usage_summary(chat_results)