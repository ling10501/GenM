FROM --platform=linux/arm64 tensorflow/tensorflow:2.9.1

WORKDIR /app

# Install necessary Python packages
RUN pip install numpy pandas matplotlib scikit-learn

# Copy your AI code into the container
COPY . /app

# Command to run your AI training script
CMD ["python", "train.py"]
