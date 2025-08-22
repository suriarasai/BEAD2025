# PySpark, MinIO, and Jupyter on Podman Desktop
This project provides a self-contained environment for running PySpark jobs with MinIO as an S3-compatible object store, all managed through Podman Desktop.

##Prerequisites
* Podman Desktop: You must have Podman Desktop installed and running on your system.
* Project Structure: You need to create the following directory structure and place the files accordingly:

.
├── data/
│   └── BEAD-Rebu_TripData.csv  <-- Place your CSV file here
├── jars/
│   ├── aws-java-sdk-bundle-1.12.262.jar
│   └── hadoop-aws-3.3.4.jar
├── notebooks/
│   └── pyspark_minio_eda.ipynb <-- The Jupyter notebook
├── podman-compose.yml
└── Dockerfile

Important: You will need to download the two .jar files and place them in the jars directory:

aws-java-sdk-bundle-1.12.262.jar

hadoop-aws-3.3.4.jar

##Step-by-Step Instructions
1. Set Up Your Project Directory
Create the folder structure as shown above and place all the provided files (docker-compose.yml, Dockerfile, pyspark_minio_eda.ipynb, and your BEAD-Rebu_TripData.csv) in their respective locations. Don't forget to download the required JAR files.

2. Launch the Environment from the Podman Command Line
   1. Open a terminal or command prompt.
   2. Navigate to your project directory (the one containing the docker-compose.yml file).
   3. Run the following command to build the images and start the services in the background:
```bash
podman compose -f podman-compose.yaml up --build
```
         

   4. You can now open Podman Desktop to see your containers running. You will see two new containers: pyspark_jupyter and minio_server.

3. Access MinIO and Jupyter
Once the containers are running:

   * MinIO Console: Open your web browser and go to http://localhost:9001.
     * Log in with the credentials:
       Access Key: minioadmin 
       Secret Key: minioadmin
   * You can use the console to view the buckets and data you create.
   * JupyterLab: Open your web browser and go to http://localhost:8888.
   * You should see the JupyterLab interface.

4. Run the PySpark Notebook
   1. In the JupyterLab file browser on the left, you should see the pyspark_minio_eda.ipynb notebook inside the work directory.
   2. Double-click to open it.
   3. Run the cells of the notebook one by one by selecting a cell and pressing Shift + Enter.

###What the Notebook Does:
   1. Initializes Spark: Sets up a SparkSession configured to communicate with the MinIO container.
   2. Creates a Bucket: Uses boto3 to create a new bucket named tripdata in MinIO (if it doesn't already exist).
   3. Reads Local CSV: Reads your BEAD-Rebu_TripData.csv file into a Spark DataFrame.
   4. Writes to MinIO: Writes the DataFrame to the tripdata bucket in the efficient Parquet file format. You can verify this by checking the MinIO console.
   5. Reads from MinIO: Reads the Parquet data from MinIO back into a new DataFrame to verify the write/read cycle.
   6. Performs EDA: Runs a few simple queries on the data to demonstrate basic analysis, such as finding the average trip distance and the most popular pickup locations.

5. Shutting Down
   1.From your terminal (in the same project directory), run the following command to stop and remove the containers:
```bash
podman compose -f podman-compose.yaml down
```
   2. This will stop and remove the containers and the network created by compose. If you want to also remove the volume containing your MinIO data, you can run
```bash
podman compose -f podman-compose.yaml down -v
```
