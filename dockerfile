# Use an official TensorFlow image that supports ARM64 architecture (suitable for M1 Mac)
FROM --platform=linux/arm64 tensorflow/tensorflow:2.9.1

# Set the working directory inside the container
WORKDIR /app

# Install additional Python packages that may be required for your project
RUN pip install --no-cache-dir numpy pandas matplotlib scikit-learn pycryptodome

# Install any additional tools or dependencies (e.g., Flask for a simple web interface)
# RUN pip install flask

# Copy the current directory contents into the container at /app
COPY . /app

# Expose any ports the application might use (e.g., if running a web server)
# EXPOSE 5000

# Command to run your Python script (this example assumes you have a script called polymorphic_malware.py)
CMD ["python", "polymorphic_malware.py"]
