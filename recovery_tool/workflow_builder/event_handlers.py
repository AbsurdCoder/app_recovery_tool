# recovery_tool/workflow_builder/event_handlers.py
import json
import yaml
# from kafka import KafkaProducer, KafkaConsumer
# import pymqi
# import psycopg2

class BaseEventHandler:
    def __init__(self, config):
        self.config = config
        
    def validate_config(self):
        """Validate that the configuration has all required fields."""
        raise NotImplementedError("Subclasses must implement validate_config")
        
    def execute(self):
        """Execute the event handler's logic."""
        raise NotImplementedError("Subclasses must implement execute")

class KafkaToKafkaHandler(BaseEventHandler):
    def validate_config(self):
        required_fields = [
            'source_bootstrap_servers', 'source_topic', 'source_group_id',
            'target_bootstrap_servers', 'target_topic'
        ]
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field: {field}")
    
    def execute(self):
        self.validate_config()
        
        # Create consumer
        consumer = KafkaConsumer(
            self.config['source_topic'],
            bootstrap_servers=self.config['source_bootstrap_servers'],
            group_id=self.config['source_group_id'],
            auto_offset_reset='earliest',
            enable_auto_commit=False
        )
        
        # Create producer
        producer = KafkaProducer(
            bootstrap_servers=self.config['target_bootstrap_servers']
        )
        
        # Process messages
        count = 0
        max_messages = self.config.get('max_messages', 100)
        
        for message in consumer:
            # Send to target topic
            producer.send(
                self.config['target_topic'],
                key=message.key,
                value=message.value
            )
            
            count += 1
            if count >= max_messages:
                break
                
        producer.flush()
        consumer.close()
        
        return f"Processed {count} messages from Kafka to Kafka"

class KafkaToMQHandler(BaseEventHandler):
    def validate_config(self):
        required_fields = [
            'source_bootstrap_servers', 'source_topic', 'source_group_id',
            'mq_queue_manager', 'mq_channel', 'mq_host', 'mq_port', 'mq_queue_name'
        ]
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field: {field}")
    
    def execute(self):
        self.validate_config()
        
        # Create Kafka consumer
        consumer = KafkaConsumer(
            self.config['source_topic'],
            bootstrap_servers=self.config['source_bootstrap_servers'],
            group_id=self.config['source_group_id'],
            auto_offset_reset='earliest',
            enable_auto_commit=False
        )
        
        # Set up MQ connection
        qmgr = pymqi.connect(
            self.config['mq_queue_manager'], 
            self.config['mq_channel'],
            f"{self.config['mq_host']}({self.config['mq_port']})"
        )
        
        queue = pymqi.Queue(qmgr, self.config['mq_queue_name'])
        
        # Process messages
        count = 0
        max_messages = self.config.get('max_messages', 100)
        
        for message in consumer:
            # Send to MQ
            queue.put(message.value)
            
            count += 1
            if count >= max_messages:
                break
                
        queue.close()
        qmgr.disconnect()
        consumer.close()
        
        return f"Processed {count} messages from Kafka to MQ"

class MQtoMQHandler(BaseEventHandler):
    def validate_config(self):
        required_fields = [
            'source_mq_queue_manager', 'source_mq_channel', 'source_mq_host', 
            'source_mq_port', 'source_mq_queue_name',
            'target_mq_queue_manager', 'target_mq_channel', 'target_mq_host', 
            'target_mq_port', 'target_mq_queue_name'
        ]
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field: {field}")
    
    # def execute(self):
    #     self.validate_config()
        
    #     # Set up source MQ connection
    #     source_qmgr = pymqi.connect(
    #         self.config['source_mq_queue_manager'], 
    #         self.config['source_mq_channel'],
    #         f"{self.config['source_mq_host']}({self.config['source_mq_port']})"
    #     )
        
    #     source_queue = pymqi.Queue(source_qmgr, self.config['source_mq_queue_name'])
        
    #     # Set up target MQ connection
    #     target_qmgr = pymqi.connect(
    #         self.config['target_mq_queue_manager'], 
    #         self.config['target_mq_channel'],
    #         f"{self.config['target_mq_host']}({self.config['target_mq_port']})"
    #     )
        
    #     target_queue = pymqi.Queue(target_qmgr, self.config['target_mq_queue_name'])
        
    #     # Process messages
    #     count = 0
    #     max_messages = self.config.get('max_messages', 100)
        
    #     while count < max_messages:
    #         try:
    #             # Get message from source
    #             message = source_queue.get()
                
    #             # Put