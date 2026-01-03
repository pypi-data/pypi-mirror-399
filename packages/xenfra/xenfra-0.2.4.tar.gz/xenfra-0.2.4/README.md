# Xenfra CLI

## Xenfra CLI: Deploy Python Apps with Zen Mode

The Xenfra CLI is a powerful and intuitive command-line interface designed to streamline the deployment of Python applications to DigitalOcean. Built with a "Zen Mode" philosophy, it automates complex infrastructure tasks, allowing developers to focus on writing code.

### ✨ Key Features

*   **Zero-Configuration Deployment:** Automatically detects your project's framework and dependencies.
*   **AI-Powered Auto-Healing:** Diagnoses common deployment failures and suggests, or even applies, fixes automatically.
*   **Real-time Monitoring:** View deployment status and stream live application logs directly from your terminal.
*   **Integrated Project Management:** Easily list, view, and destroy your deployed projects.
*   **Secure Authentication:** Uses OAuth2 PKCE flow for secure, token-based authentication.

### 🚀 Quickstart

#### 1. Installation

Install the Xenfra CLI using `uv` (recommended) or `pip`:

```bash
uv pip install xenfra-cli
# or
pip install xenfra-cli
```

#### 2. Authentication

Log in to your Xenfra account. This will open your web browser to complete the OAuth2 flow.

```bash
xenfra auth login
```

#### 3. Initialize Your Project

Navigate to your Python project's root directory and run `init`. The CLI will scan your codebase, detect its characteristics, and generate a `xenfra.yaml` configuration file.

```bash
cd your-python-project/
xenfra init
```

#### 4. Deploy Your Application

Once `xenfra.yaml` is configured, deploy your application. The CLI will handle provisioning a DigitalOcean Droplet, setting up Docker, and deploying your code.

```bash
xenfra deploy
```

### 📋 Usage Examples

*   **Monitor Deployment Status:**
    ```bash
    xenfra status <deployment-id>
    ```
*   **Stream Application Logs:**
    ```bash
    xenfra logs <deployment-id>
    ```
*   **List Deployed Projects:**
    ```bash
    xenfra projects list
    ```
*   **Diagnose a Failed Deployment (AI-Powered):**
    ```bash
    xenfra diagnose <deployment-id>
    # Or to diagnose from a log file:
    xenfra diagnose --logs error.log
    ```

### 📚 Documentation

For more detailed information, advanced configurations, and API references, please refer to the [official Xenfra Documentation](https://docs.xenfra.com/cli) (Link will be updated upon final deployment).

### 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details.

### 📄 License

This project is licensed under the [MIT License](LICENSE).
