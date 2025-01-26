# Quiz Performance Analysis System

A Dockerized application that analyzes quiz performance data, generates insights, and provides AI-powered recommendations using Groq's API.

## Features

- 📊 Performance analysis by topic and difficulty level
- 📈 Historical trend tracking across last 5 quizzes
- 🤖 AI-powered personalized recommendations (Groq API)
- 🐳 Docker container support for easy deployment
- 🔍 Automatic data validation and error handling

## Prerequisites

- Docker installed
- Groq API key (free at [Groq Cloud](https://console.groq.com/keys))

## Installation


# Clone the repository
```
git clone [https://github.com/Yash/quiz-analysis.git](https://github.com/Yash-200/Quiz-t.git)
cd quiz-analysis
```

# Build the Docker image
```
docker build -t quiz-analysis .
```
```
docker run -it \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -e QUIZ_URL="your_quiz_url" \
  -e SUBMISSION_URL="your_submission_url" \
  quiz-analysis
```
