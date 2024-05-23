# CITS5505-Group-Project
## Group Members

<div align="center">

| Student ID | Name      | Github Username |
| ---------- | --------- | --------------- |
| 23954248   | Zhang Chi | MomobamiKiraly  |
| 24125299   | Yu Xia    | dayday0calories |
| 23957505   | Zongqi Wu | jacky-zq-woo    |
| 23895642   | Yi Ren    | lingering126    |

</div>
<div align="center">

<h1 align="center">SpeedSters (A World of Fancy Cars)</h1>

</div>

Welcome to the **SpeedSters**, the premier online destination for car lovers in this globe! This web application is designed to foster a vibrant community where users can share their beloved cars, discuss various car-related topics, and access a wealth of latest car-related news from worldwide. Whether you're looking to show off your beloved cars, seek advice for buying a car, or find a event you are interested to join, **SpeedSters** is your go-to hub for all things cars only.

## Features

- **Community Discussions & Interactive Posts**: Engage in discussions on a wide range of car-related topics,share latest releases, ask questions about cars, and interact with fellow cars owners.
- **Car Dealing Information**: Post and browse car dealing listings, help you choose your beloved one.
- **AI Intelligent Car Assistant**:With AI, you can get the information you want about automobiles answered in a timely manner.




## Instructions for Running the Application

To get started with **SpeedSters**, follow these steps:

1. **Clone the repository**:
   ```sh
   git clone https://github.com/dayday0calories/CITS5505-Group-Project
2. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
3. **Run the project**
   ```sh
   flask run
    * Running on http://127.0.0.1:5000
    ```

#### If the program does not run properly, check the following steps:


1. **Check Python Installation:** Verifies if Python3 is installed on the system,if not,install latest Python version.
2. **Check Flask Installation:** Checks if Flask is installed globally and, if absent, attempt to install it.
3. **Virtual Environment Management:** If a virtual environment  does not exist, create one using Python3.
4. **Dependency Installation:** Ensures a `requirements.txt` file is present and installs all dependencies listed.
5. **Check Port Availability:** Checks if the specified port is available. 



#### Shutdown the Application
Simply run:
```bash

Ctrl + C
```

## Instructions for Running the Tests
Download ChromeWebdriver, add the installing path to environment variable.

Then run the app using
```sh
   flask run
    * Running on http://127.0.0.1:5000
```
Then open a new terminal, run
```bash

python -m unittest discover -s tests
```



