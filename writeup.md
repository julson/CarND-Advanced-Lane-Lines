** Advanced Lane Finding Project **

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

[distorted]: ./camera_cal/calibration1.jpg "Distorted
[undistorted]: ./examples/undistort_output.png "Undistorted"
[original]: ./test_images/test1.jpg "Road Transformed"
[threshold]: ./examples/binary.jpg "Binary Example"
[straight]: ./text_iamges/straight_lines1.jpg "Straight Lane"
[warped]: ./examples/warped_straight_lines.jpg "Warp Example"
[test4]: ./test_images/test4.jpg "Test 4"
[pipeline]: ./examples/pipeline.jpg "Pipeline Result"
[curve]: ./examples/curve_fit.jpg "Fit Visual"
[output]: ./examples/final.jpg "Output"
[video1]: ./project_video_out.mp4 "Video"

### Camera Calibration

The first step of the pipeline involves correcting for camera distortion. I did this by running chessboard corner detection across all calibration images, using a set of object points fixed on the (x, y) plane at z=0 and storing the images points for images where corners were detected.

Distortion coefficients and the camera metrix  are then obtained by feeding this into OpenCV's `cv2.calibrateCamera()` method. These gives us enough to run `cv2.undistort`. We can now use one of the calibration images as our guinea pig for undistortion. For example, running undistortion from this:

![alt text][undistorted]

gives us this result:

![alt text][distorted]

### Color Thresholding

Thresholding (`apply_threshold()`) was implemented by first converting the image into the HLS colorspace, which is a better representation since it isolates the hue (which we don't need for lane lines). The L-channel gives us a grayscale representation of the image which I used the Sobel filter for to obtain the gradient edges. The S-channel gives us a more black and white image, and we use a simple binary threshold to isolate light colored lines. We then combine them into one image for the next steps.

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

![alt text][final]

### Pipeline (Video)

We run the pipeline through each frame of the project video. A text overlay also shows the estimated curve radius and position from center. Here's the [link](./project_video_out.mp4).

### Discussion

There were a lot of problems encountered when running the pipeline on the video (I didn't have time to address them all). First, the sliding window search would oftentimes not find any lane at all on a particular frame (especially on segmented lane lines). This throws off polynomial curve fitting and causes the visualization to create a different lane of its own. I mitigate this by only doing a sliding search on the first frame and using `next_fit()` to make minor adjustments so the visualizations will not be far off. I'm also keeping track of the previous frame's fits and throwing away any fits if the combined curve radius of both lanes exceeds a certain amount.

This is extremely rudimentary, but it does the job somewhat. A much more ideal solution in this case would be to keep track of a certain set of previous fits to get a better curve estimation. It
also needs more forms of error detection (i.e. lane is not detected) and correction (i.e. apply sliding window search again).

There's also a problem where pixels from cars sneak into the windows and causes the subsequent windows to latch onto them, thereby creating a false lane. I think the masking technique from the previous lane finding project will help in this regard. More robustly, being able to identify cars and subtracting them from the image would be a huge help too.

I didn't get the chance to explore other forms of thresholding or colorspaces. There might be some more techniques there that would help isolate the lane lines.
