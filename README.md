![](https://img.shields.io/badge/Microverse-blueviolet)

# Cookbook Chatbot

This cookbook chatbot is an interactive culinary assistant designed to guide users through recipes and cooking techniques inspired by Christine Ha's acclaimed cookbook. By combining advanced AI with rich culinary content, the chatbot helps users master new dishes and build confidence in the kitchen


## Built With

- LlamaIndex
- Langchain
- Chainlit

## Live Demo 

in progess :smile:


## Getting Started


To get a local copy up and running follow these simple example steps.

### Prerequisites
Ensure you have the following installed on your system:  
- **Python 3.9+**  
- **Anaconda or Miniconda** for managing environments  
- Access to the **OpenAI API key** (store it securely in a `.env` file)  

---

### Setup
1. Clone this repository to your local machine:  
   ```bash  
   git clone <repository-url>  
   cd <project-folder>
   ```
2. Create and activate a new Anaconda environment:
   ```bash
   conda create -n cookbook_bot python=3.12
   conda activate cookbook_bot
   ```

---

### Install
Install the required Python libraries using pip:
  ```bash
  pip install llama-index openai langchain literalai chainlit python-dotenv
  ```
---

### Usage
1. Add your OpenAI API key and other keys to a .env file in the root directory:
   ```plaintext
   OPENAI_API_KEY ="your - openai -api - key "
   LLAMA_CLOUD_API_KEY ="your -llama -cloud -api -key "
   LITERAL_API_KEY ="your - literalai -api -key"
   OAUTH_GOOGLE_CLIENT_ID ="your -oauth -google -client -id"
   OAUTH_GOOGLE_CLIENT_SECRET ="your -oauth -google -client - secret "
   CHAINLIT_AUTH_SECRET ="your - chainlit -auth - secret - key"
   ```
2. Start the chatbot application using Chainlit:
   ```bash
   chainlit run app.py -w
   ```
3. Open your browser to access the chatbot interface at http://localhost:8000

---

### Deployment
1. Ensure the environment is set up on your production server.
2. Follow the same installation and usage steps.
3. Optionally, deploy using a platform like Docker, Heroku, or AWS Lambda for easier scaling.

---

## Authors

👤 **Nguyen Minh Tri**

- GitHub: [@turtle6814](https://github.com/turtle6814)
- LinkedIn: [Minh Trí Nguyễn](https://www.linkedin.com/in/tringuyen14/)

👤 **Vuong Quoc An**

- GitHub: [@QuocAnVuong](https://github.com/QuocAnVuong)
- LinkedIn: [Vuong Quoc An](https://www.linkedin.com/in/vuong-quoc-an-8b0b28269/)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
