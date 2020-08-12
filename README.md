# Local Laplacian Filter

This is a try to implement the Local Laplacian Filters, Edge-aware Image Processing with a Laplacian Pyramid in Python [1]. Moreover project has the basic GUI for comparison purposes like also image quality assessment using selected metrics. App allows to save metric scores, parameter settings, output image to SQLite3 DB which is automatically created during first run. Requirements about modules are contained in requirements.txt.

## Results

Original        |  Enhanced
:-------------------------:|:-------------------------:
![Input_image](/Images/flower.png)  |  ![Output_image](/Images/flower_enhanced.png)
![Input_image](/Images/easter.png)  |  ![Output_image](/Images/easter_enhanced.png)


## GUI
App allows to load and compare two images, the input and enhanced one by using different quality metrics like BRISQUE, MSE, PSNR, SSIM, GMSD. User is able to set paramaters alpha, beta and sigma_r to obtain different effects of output image (DEFAULT button is related to parameters defined in .ini file). Session might be saved to DB by using disk icon. LCD display shows the information about layer number of Laplacian Pyramid is actually processed and the overall time needed for computing.

![Input_image](/Images/app.png)


1. S. Paris, S.W. Hasinoff, J.Kautz, “Local Laplacian Filters: Edge-aware Image Processing with a Laplacian Pyramid”, Communications of the ACM, March 2015, Vol. 58, Nr 3, January 2011. https://cacm.acm.org/magazines/2015/3/183587-local-laplacian-filters/abstract

2. (Images source) https://people.csail.mit.edu/sparis/publi/2011/siggraph/, http://www.cs.albany.edu/~xypan/research/snr/Kodak.html
