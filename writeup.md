# Advanced Lane Finding Project

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

[//]: # (Image References)

[distorted]: ./camera_cal/calibration1.jpg "Distorted"
[undistorted]: ./examples/undistort_output.png "Undistorted"
[original]: ./test_images/test1.jpg "Road Transformed"
[threshold]: ./examples/binary.jpg "Binary Example"
[straight]: ./test_images/straight_lines1.jpg "Straight Lane"
[warped]: ./examples/warped_straight_lines.jpg "Warp Example"
[test4]: ./test_images/test4.jpg "Test 4"
[pipeline]: ./examples/pipeline.jpg "Pipeline Result"
[curve]: ./examples/curve_fit.jpg "Fit Visual"
[output]: ./examples/final.jpg "Output"
[video1]: ./project_video_out.mp4 "Video"

### Camera Calibration

The first step of the pipeline involves correcting for camera distortion. I did this by running chessboard corner detection across all calibration images, using a set of object points fixed on the (x, y) plane at z=0 and storing the images points for images where corners were detected.

Distortion coefficients and the camera metrix  are then obtained by feeding this into OpenCV's `cv2.calibrateCamera()` method. These gives us enough to run `cv2.undistort`. We can now use one of the calibration images as our guinea pig for undistortion. For example, running undistortion from this:

![alt text][distorted]

gives us this result:

![alt text][undistorted]

### Color Thresholding

Thresholding (`apply_threshold()`) was implemented by first converting the image into the HLS colorspace, which is a better representation since it isolates the hue (which we don't need for lane lines). The L-channel gives us a grayscale representation of the image which I used the Sobel filter for to obtain the gradient edges. The S-channel gives us a more black and white image, and we use a simple binary threshold to isolate light colored lines. We then combine them into one image for the next steps.

#### Update:

Using gradients to isolate lane lines was a bit more error-prone and gave a more noisy binary image, so I played around with other colorspaces such as HSV, Lab and Luv. I ultimately settled with Luv's L-channel and HLS's L-channel to isolate white lines and Lab's b-channel to isolate yellow lines.


![alt text][original]
![alt text][threshold]

### Perspective Transform

The `top_perspective()` method is responsible for obtaining the top perspective view of the image.
The transform is performed by using a set of source points that form an overlay over the road and a set of destination points that represent the top view of the road.

| Source      | Destination    |
|:-----------:|:---------------|
|575, 464     |450, 0          |
|707, 464     |830, 0          |
|258, 682     |450, 720        |
|1049, 682    |830, 720        |

![alt text][straight]
![alt text][warped]

Combining all the previous techniques produces something like this:

![alt text][test4]
![alt text][pipeline]

### Identifying Lanes

`sliding_window_fit()` and `next_fit()` methods work to identify the lanes in the image. `sliding_window_fit()` obtains the histogram of the image and divides it into several layers. A small window is applied at locations in the image where the lanes are most likely to be found in order to constrain the search space, and the window is moved in subsequent search once the lane pixels reach a threshold. These lane pixels are then fit through a 2nd order polynomial to determine the coefficients. The difference between the 2 methods is that `next_fit()` uses the previous found pixels to adjust the coefficients instead of doing a full search

Visualizing the sliding windows and lane curves gives us this:

![alt text][curve]

### Curve Radius and Position from Center

These are calculated by the `curve_radius()` and `center_position()` methods. We convert the pixel measurements into meters using a predetermined ratio (3.7 meters per 700 pixels in x, 30 meters per 720 pixels in y)

### Warping the Measurements Back

Given the estimated curvature of the lane, we then apply the visualization back to the original road image to show where we think the lane is.

![alt text][output]

### Pipeline (Video)

We run the pipeline through each frame of the project video. A text overlay also shows the estimated curve radius and position from center. Here's the [link](./project_video_out.mp4).

I ran the perspective transform first before the thresholding operation, so that the error pixels don't get amplified and I end up with a less noisy image.

We keep track of at most five good fits for each line just in case a subsequent line is not detected. This provides for a smoother lane estimate. As far as error detected goes, I'm keeping thresholds of curve changes from prior estimates and doing a rough estimate if both lines are parallel by comparing the distance between both ends and their respective centers.

### Discussion

While this is a satisfactory implementation, there are a few problems that arose, especially on the challenge videos. Static thresholding is not directly transferrable, since it might have been overfitted to certain brightness and contrast values, so there needs to be a way to do some sort of adaptive thresholding based on certain image metrics. I tried playing around with histogram equalization and OpenCV's adaptive thresholding functions, but it didn't yield good results.

It's also subject to sudden video changes like bumps, glare or reflection which can be dealt with through better error detection and keeping track of prior fits (and determining whether or not to take advantage of them).
