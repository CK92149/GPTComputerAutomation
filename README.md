
GPTComputerAutomation
=====================

GPTComputerAutomation is a tool that leverages OpenAI's GPT-4o model to analyze screenshots and UI elements, automating mouse clicks and typing actions on your computer.

![Demo of the project](assets/example%201.gif)

[Full demo on x.com](https://twitter.com/Charles12509909/status/1796541659628638587

Features
--------

- **UI Element Capture**: Recursively captures visible, clickable UI elements with their coordinates.
- **Screenshot Functionality**: Takes and encodes screenshots for analysis.
- **GPT Integration**: Uses GPT-4o to intelligently determine the next click or typing action based on UI analysis.
- **Automation Execution**: Performs the determined actions on your computer, mimicking user interaction.

Getting Started
---------------

### Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed on your machine
- Pip (Python package installer)
- Git (for cloning the repository)

### Installation

1. **Clone the Repository**

   ```sh
   git clone https://github.com/CK92149/GPTComputerAutomation.git
   cd GPTComputerAutomation
   ```sh

2. **Install the Dependencies**

   ```sh
   pip install -r requirements.txt
   ```sh

3. **Set Up Environment Variables**

   Create a `.env` file in the root directory and add your OpenAI API key:

   ```sh
   API_KEY=your_api_key_here
   ```sh

Usage
-----

1. **Run the Application**

   ```sh
   python main.py
   ```sh

2. **Interact with the GUI**

   - Enter your request in the input field.
   - Click "Perform Action" to let GPT analyze the UI elements and determine the next action.


Example Workflow
----------------

1. **Capture UI Elements**

   The tool captures visible and clickable UI elements on the screen, saving them to a file (`ui_elements.txt`).

2. **Take a Screenshot**

   A screenshot is taken and saved as `screenshot.png`, then encoded to base64 for analysis.

3. **Analyze with GPT**

   The base64-encoded screenshot and UI elements are sent to the GPT model to determine the most likely next action.

4. **Perform the Action**

   The determined action (mouse click or typing) is performed on your computer.


License
-------

This project is licensed under the MIT License - see the LICENSE file for details.


Contact
-------

If you want to contact me, you can reach me on x.com @Charles12509909
