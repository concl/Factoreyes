# Factoreyes
Checks for repetitiveness in homework.

## Our website
https://factor-zengkc.pythonanywhere.com/

## Hosting it locally
Originally our project was suppose to a website but, the hosting service may be a bit unreliable. So, in the github we left all the necessary files to run the website locally. The most important files are the static folder(images), template folder (html/css), ball.pt (our ML model), users.sqlite3 (this would theoretically be used to for a login page), and main.py. Every other file shouldn't play a role in whether it runs or not.

Main.py is the primary file and there are a fair bit of libraries that you need download. Expect to install the following:
* flask
* pytorch
* easyocr
* pix2tex
* pillow


If you do it correctly running main.py should give you something like the following.

<img src="website1.png" alt="website" title="webstite">

You can configure your tolerance values and press update to officially change settings. Then, you can drag and drop an image of quadratic factoring problems (with leading coefficient = 1) and upload the file to start the analysis. It may take a while but, the website should give you back an image with bounding boxes around the items it thinks are similar. Our program also only works with latex or other math typsetted problems, so handwritten problems will not work.
## The Primary Algorithim
Our project uses a machine learning algorithim to identify problems which have similar solutions to one another. For this task we used a recusive neural network (RNN, not to be confused with a recurrent neural network).

### Gathering Data
Due to the time constraints, we were only able to train the network on quadratic factoring problems (which may make using a recursive neural network obsolete, although its still able to generalize better to other problems). Our project centers around identifying and classifiying factoring problems. We developed a method of generating labeled quadratic factoring problems to train the network on, which could in theory be used for more complicated but still repetitive problems.

First, we generate a Latex string and then we used sympy to turn it into a parsed string since our machine learning project relied the input being in the form of a binary tree. We took the parsed string and turned it into a binary tree. For the quadratic x^2 + 3x -4 it might look like the following.

<img src="tree1.png" alt="tree image" title="tree image">

The algorithm for turning expressions into a tree doesn't stop with polynomials. It also allows for more advanced functions. Below is the following binary tree for sin(3x)/ln(x!)

<img src="tree2.png" alt="tree image" title="tree image">
