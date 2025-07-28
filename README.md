# Health Analysis API - FastAPI Backend

A sophisticated FastAPI-based backend service that provides comprehensive, AI-powered health analysis through a multi-agent system. The platform delivers personalized nutrition plans, behavioral analysis, and routine recommendations based on user health data and selected personality archetypes.

## 🚀 Features

- **Real-time Analysis**: Server-Sent Events (SSE) for live progress updates
- **Multiple Archetypes**: 6 different personality-based analysis approaches
- **AI-Powered**: OpenAI GPT integration for intelligent health insights
- **Console Logging**: Maintains all existing rich console output
- **Scalable**: Built with FastAPI for high performance and scalability
- **Deploy Ready**: Configured for easy deployment on Render, Heroku, etc.

## 📋 Requirements

- Python 3.12+
- PostgreSQL database
- OpenAI API key

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Health-agent
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   # Copy the example file
   cp env.example .env
   
   # Edit .env file with your actual values
   nano .env  # or use your preferred editor
   ```

   **Required .env file contents:**
   ```env
   # Database Configuration
   DATABASE_URL=postgresql://username:password@localhost:5432/health_analysis
   
   # OpenAI API Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Optional: Set to development or production
   NODE_ENV=development
   ```

## 🔧 Local Development

1. **Start the FastAPI server**:
   ```bash
   python app.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Test the analysis directly**:
   ```bash
   python main_api.py AWHDs3b6DMhhywvMwZkFZh2Byka2 "Foundation Builder"
   ```

3. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health
   - OpenAPI Schema: http://localhost:8000/openapi.json

## 🌐 API Endpoints

### GET `/`
- **Description**: Root endpoint
- **Response**: Health status

### GET `/api/health`
- **Description**: Health check endpoint
- **Response**: API operational status

### POST `/api/analyze`
- **Description**: Start health analysis with real-time updates
- **Body**:
  ```json
  {
    "user_id": "string",
    "archetype": "string"
  }
  ```
- **Response**: Server-Sent Events stream
- **Supported Archetypes**:
  - Foundation Builder
  - Transformation Seeker
  - Systematic Improver
  - Peak Performer
  - Resilience Rebuilder
  - Connected Explorer

### GET `/api/status`
- **Description**: Get current API status and active processes
- **Response**: Status information

## 🌟 Archetypes

1. **Foundation Builder** 🏗️
   - Simple, sustainable basics for beginners

2. **Transformation Seeker** 🚀
   - Ambitious individuals ready for major changes

3. **Systematic Improver** 🔬
   - Detail-oriented, methodical approach

4. **Peak Performer** 🏆
   - High-achieving individuals seeking optimization

5. **Resilience Rebuilder** 🌱
   - Gentle restoration and recovery focus

6. **Connected Explorer** 🌍
   - Social connection and adventure-oriented

## 📱 Frontend Integration

The API is designed to work with the React frontend. Update the frontend's API base URL:

```javascript
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-render-app.onrender.com'
  : 'http://localhost:8000';
```

## 🚀 Deployment

### Render Deployment

1. **Create .env file** with your actual values:
   ```env
   DATABASE_URL=postgresql://username:password@host:5432/database
   OPENAI_API_KEY=your_actual_openai_api_key
   ```

2. **Connect your repository** to Render

3. **Set environment variables in Render dashboard**:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `OPENAI_API_KEY`: Your OpenAI API key

4. **Deploy**: Render will automatically use `render.yaml` configuration

### Manual Deployment

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export PORT=8000
   export DATABASE_URL="your-database-url"
   export OPENAI_API_KEY="your-openai-api-key"
   ```

3. **Start the server**:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

## 🔐 Environment Variables

| Variable         | Description                  | Required | Example                                    |
| ---------------- | ---------------------------- | -------- | ------------------------------------------ |
| `DATABASE_URL`   | PostgreSQL connection string | Yes      | `postgresql://user:pass@localhost:5432/db` |
| `OPENAI_API_KEY` | OpenAI API key               | Yes      | `sk-...`                                   |
| `PORT`           | Server port (default: 8000)  | No       | `8000`                                     |
| `NODE_ENV`       | Environment mode             | No       | `development`                              |

## 🔍 Environment Variable Loading

The application automatically searches for `.env` files in the following order:
1. `Health-agent/.env` (current directory)
2. `../.env` (parent directory)
3. Current working directory

If no `.env` file is found, it will use system environment variables.

## 🏗️ Architecture

- **FastAPI**: Modern, fast Python web framework
- **Uvicorn**: ASGI server for production
- **Server-Sent Events**: Real-time streaming updates
- **Subprocess Management**: Executes analysis agents
- **CORS**: Cross-origin resource sharing enabled
- **Environment Loading**: Flexible .env file detection

## 🔧 Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
```

### Linting
```bash
flake8 .
```

## 📊 Monitoring

The API includes built-in monitoring for:
- Active analysis processes
- Connection status
- Error tracking
- Performance metrics

## 🐛 Troubleshooting

### Common Issues

1. **Environment Variables Not Loading**:
   - Check if `.env` file exists: `ls -la .env`
   - Verify file contents: `cat .env`
   - Use `env.example` as template
   - Ensure no extra spaces or quotes around values

2. **Database Connection Error**:
   - Check `DATABASE_URL` format: `postgresql://user:pass@host:port/db`
   - Ensure PostgreSQL is running
   - Verify database exists

3. **OpenAI API Error**:
   - Check `OPENAI_API_KEY` is valid
   - Verify API usage limits
   - Test with OpenAI CLI: `openai api models`

4. **Port Already in Use**:
   - Change port: `uvicorn app:app --port 8001`
   - Kill existing process: `lsof -ti:8000 | xargs kill`

5. **Missing Dependencies**:
   - Reinstall: `pip install -r requirements.txt`
   - Update pip: `pip install --upgrade pip`

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🤝 Support

For support, please open an issue in the GitHub repository. 