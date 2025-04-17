# Dynamic Recovery Tool

![Dynamic Recovery Tool](https://img.shields.io/badge/Version-1.0.0-blue)
![Django](https://img.shields.io/badge/Django-4.2-orange)
![Python](https://img.shields.io/badge/Python-3.8+-yellow)

A visual workflow builder for creating and automating data recovery and migration processes across multiple infrastructure systems.

![Recovery Tool Preview](https://i.imgur.com/placeholder.png)

## 🌟 Features

- **Visual Workflow Builder**: Create recovery workflows with an intuitive UI
- **Multiple Infrastructure Support**: Connect to Kafka, MQ, databases, service buses, and file systems
- **Dynamic UI Components**: Configurable steps with context-aware options
- **YAML Generation**: Auto-generated YAML configurations for versioning and portability
- **Real-time Execution Tracking**: Interactive UI showing workflow execution progress
- **Extensible Design**: Easy to add new event types and infrastructure connections

## 📋 Table of Contents

- [Installation](#-installation)
- [Usage](#-usage)
- [Workflow Types](#-workflow-types)
- [Infrastructure Types](#-infrastructure-types)
- [Configuration](#-configuration)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Setup

1. Clone the repository:

```bash
git clone https://github.com/your-username/recovery-tool.git
cd recovery-tool
```

2. Create and activate a virtual environment:

```bash
python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up the database:

```bash
cd recovery_tool
python manage.py migrate
```

5. Create a superuser:

```bash
python manage.py createsuperuser
```

6. Run the server:

```bash
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/

## 🎮 Usage

### Creating a Workflow

1. Navigate to the dashboard
2. Click "Create New Workflow"
3. Enter a name and description
4. Add steps to the workflow:
   - Select event type (Replay, Dump, Extract, Transform, Load)
   - Configure source and destination infrastructure
   - Enter connection details
5. Save the workflow

### Executing a Workflow

1. Navigate to the workflow list
2. Click the "Execute" button for the workflow you want to run
3. Monitor the execution progress in real-time
4. View logs and results when execution completes

## 🔄 Workflow Types

The tool supports the following event types:

| Event Type | Description | Required Sections |
|------------|-------------|-------------------|
| Replay | Move data from one system to another | From, To |
| Dump | Extract data from a system without a specific destination | From only |
| Extract | Targeted extraction of specific data | From only |
| Transform | Read data, apply transformations, and write to a destination | From, To |
| Load | Load data into a target system | To only |

## 🏗️ Infrastructure Types

The following infrastructure types are supported:

| Type | Description | Examples |
|------|-------------|----------|
| Kafka | Apache Kafka streams | Topics, consumer groups |
| MQ | IBM MQ or other message queues | Queues, topics |
| Database | SQL and NoSQL databases | PostgreSQL, MySQL, MongoDB |
| Service Bus | Cloud messaging services | Azure Service Bus, AWS SQS |
| File System | Local or network file storage | CSV, JSON, XML files |

## ⚙️ Configuration

### External Systems

For connecting to external systems, you'll need to update the appropriate configuration based on your environment:

#### Kafka

```yaml
bootstrap_servers: kafka:9092
topic: my-topic
group_id: recovery-group
```

#### Database

```yaml
db_type: postgresql
host: localhost
port: 5432
username: dbuser
password: dbpass
database: mydb
```

See the documentation for more configuration examples.

## 💻 Development

### Project Structure

```
recovery_tool/
├── manage.py
├── recovery_tool/         # Project settings
└── workflow_builder/      # Main application
    ├── models.py          # Data models
    ├── views.py           # View controllers
    ├── urls.py            # URL routing
    ├── templates/         # UI templates
    ├── static/            # Static assets
    └── event_handlers.py  # Execution logic
```

### Adding New Event Types

1. Update `WorkflowStep.EVENT_TYPES` in `models.py`
2. Add handling logic in the JavaScript UI
3. Implement the handler in `event_handlers.py`

### Adding New Infrastructure Types

1. Update `WorkflowStep.INFRA_TYPES` in `models.py`
2. Add configuration fields to the UI
3. Implement connection logic in the appropriate handlers

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure to update tests as appropriate.

## 📜 License



## 📬 Contact

Your Name - absurdcoder@gmail.com

---

Made with ❤️ by AbsurdCoders
