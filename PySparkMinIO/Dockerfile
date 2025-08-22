# Dockerfile
# This file is used to build a custom Docker image for our PySpark service.
# It starts from a pre-built Jupyter image with Spark and adds the necessary dependencies.

# Use a base image with Jupyter and Spark pre-installed
FROM jupyter/pyspark-notebook:latest

# Switch to root user to install packages
USER root

# Install necessary packages
# We are installing hadoop-aws and aws-java-sdk-bundle which are required for S3A filesystem client
RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Add Spark and Hadoop related environment variables and JARs for MinIO
# These JARs are crucial for Spark to be able to communicate with an S3-compatible store like MinIO.
ENV SPARK_HOME /usr/local/spark
ENV HADOOP_HOME /usr/local/hadoop
ENV PATH $PATH:$SPARK_HOME/bin:$HADOOP_HOME/bin

COPY --chown=${NB_UID}:${NB_GID} jars/aws-java-sdk-bundle-1.12.262.jar ${SPARK_HOME}/jars/
COPY --chown=${NB_UID}:${NB_GID} jars/hadoop-aws-3.3.4.jar ${SPARK_HOME}/jars/

# Switch back to the default notebook user
USER ${NB_UID}

# Install Python libraries
RUN pip install --no-cache-dir \
    pyspark==3.4.1 \
    boto3

# Expose ports for Jupyter and Spark UI
EXPOSE 8888 4040

# Command to start JupyterLab
CMD ["start-notebook.sh", "--NotebookApp.token=''"]
