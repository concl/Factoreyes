# Factoreyes
Checks for repetitiveness in homework.

## How to use it
Originally our project was suppose to a website but, we were unable to set it up. So, in the github we left all the necessary files to run the website locally. The most important files to upload is the static folder(images), template folder (html/css), ball.pt (our ML model), users.sqlite3 (this would theoretically be used to for a login page), and main.py. Every other file shouldn't play a role in whether it runs or not.

Main.py is the primary file and there are a fair bit of libraries that you need download. If you do it correctly running main.py should give you something like the following.

<img src="website1.png" alt="website" title="webstite">

## The Primary Algorithim
Our project uses a machine learning algorithim to identify problems which have similar behaviors to one another. For this task we used a RNN (recursive neural network).

### Gathering Data
For this hackathon we chose to primarily focus on only one type of math problems. We chose to center our project around identifying, classifiying, and analyzing factoring problems. For our machine learning algorithim to work we needed data to train it off of. We focusing on factoring problems but, the way we generated the data for the RNN was more general.

First, we created a generate a Latex string and then we used sympy to turn it into a parsed string. Since, our machine learning project relied the input being in the form of a binary tree. We took the parsed string and turned it into a binary tree. For the quadartic x^2 + 3x -4 it might look like the following.

<img src="tree1.png" alt="tree image" title="tree image">

Our algorithim for turning expressions into tree doesn't stop with polynomials. It also allows for more advanced functions. Below is the following binary tree for sin(3x)/ln(x!)

<img src="tree2.png" alt="tree image" title="tree image">
