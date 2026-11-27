# ruff: noqa: ISC004 — dữ liệu đề: chuỗi dài ngắt dòng trong danh sách là cố ý
"""Đoạn tri thức khóa 494 — ĐỢT 3 (27/11/2026): Module 4 "Data Analysis for IoT" của khóa (IIT Bombay).
Bám đề cương công khai (tên video): Why Data Analysis for IoT? · Components and Feasibility of Learning · Types of
Learning · Data-Driven Techniques · Practical Implementation with Python · Introduction to Linear Regression · Time-Series
Data · Time-series model · Introduction to Clustering (+ các video thực hành Python). Mức nhập môn: không công thức xác
suất (Hoeffding), không viết code; phần "Components and Feasibility of Learning" giả định theo khung Learning From Data."""

CHUNKS_B3 = [
    (
        "DA",
        "Why data analysis for IoT",
        "IoT systems produce very large amounts of data: many sensors report readings continuously, often every few "
        "seconds, and the data comes in many forms, such as temperatures, vibrations, images and logs. Raw readings are "
        "of little use until they are analysed. Data analysis turns them into information and decisions. Typical goals "
        "are monitoring (showing the current state of a system on a dashboard), prediction (for example predicting a "
        "machine failure before it happens, called predictive maintenance, or forecasting energy demand), anomaly "
        "detection (finding readings that do not fit the normal pattern, such as a sudden temperature spike that may "
        "mean a fault or an attack) and automation (letting the system act by itself, such as switching irrigation on "
        "when the soil is predicted to be dry). Because the rules behind the data are often unknown or too complex to "
        "write by hand, IoT data analysis often uses machine learning, which learns a model from the data itself.",
    ),
    (
        "DA",
        "Components and feasibility of learning",
        "Learning from data can be described with a few components. There is an unknown target function f that maps an "
        "input x (for example the vibration readings of a motor) to an output y (for example whether the motor will "
        "fail soon). We do not know f, but we have a data set of examples (x, y) collected in the past. A learning "
        "algorithm searches a hypothesis set, the family of candidate models it is allowed to choose from (for example "
        "all straight lines), and picks the final hypothesis g that fits the data best, hoping that g is close to f. "
        "Learning is feasible, in a probabilistic sense, when the data are representative of the situations where the "
        "model will be used and there are enough examples: then a model that does well on the training data is likely "
        "to do well on new data too. The error on the training data is the in-sample error; the error on new, unseen "
        "data is the out-of-sample error. These terms (target function, hypothesis set, final hypothesis, in-sample "
        "and out-of-sample error) come from the widely used Learning From Data framework; other courses may simply "
        "call the final hypothesis the trained model. A model that is too complex can fit the training data almost perfectly, "
        "including its noise, yet perform badly on new data; this is called overfitting.",
    ),
    (
        "DA",
        "Types of learning and data-driven techniques",
        "There are three main types of learning. In supervised learning, every training example has the correct answer "
        "(a label): if the output is a number it is regression, for example predicting tomorrow's energy use, and if "
        "it is a category it is classification, for example faulty or normal. In unsupervised learning, the data has "
        "no labels and the algorithm looks for structure by itself, for example clustering similar devices. In "
        "reinforcement learning, an agent learns by trial and error from rewards, for example a thermostat that "
        "learns a schedule from comfort feedback. A data-driven project follows a pipeline: collect the data; clean it "
        "by handling missing values and removing or correcting outliers caused by faulty sensors; choose or compute "
        "features, such as the average vibration over a minute; split the data into a training set to fit the model "
        "and a test set, kept aside, to check how well it works on unseen data; train the model; and evaluate it. In "
        "Python, NumPy handles arrays of numbers, pandas handles tables of data such as sensor logs, scikit-learn "
        "provides models such as linear regression and k-means, and matplotlib draws plots.",
    ),
    (
        "DAT",
        "Linear regression",
        "Linear regression models the relationship between an input x and a numeric output y with a straight line, "
        "y = w0 + w1 x, where w0 is the intercept (the value of y when x is 0) and w1 is the slope (how much y changes "
        "when x increases by 1). The line is fitted by least squares: the weights are chosen to minimise the mean "
        "squared error (MSE), the average of the squared differences between the predicted and the actual values. For "
        "example, if the fitted line is y = 1.5 + 0.2 x, an input of x = 10 gives a prediction of 1.5 + 0.2 x 10 = "
        "3.5. The model is evaluated on test data, for example with the MSE: a smaller MSE means better predictions. A "
        "fitted line should only be trusted within the range of inputs it was trained on; predicting far outside "
        "that range is extrapolation and can be badly wrong, because the relationship may not stay linear.",
    ),
    (
        "DAT",
        "Time-series data and models",
        "A time series is a sequence of measurements taken in time order, usually at regular intervals, such as a "
        "temperature reading every hour. A time series is often described by three components: the trend, a long-term "
        "increase or decrease; seasonality, a pattern that repeats with a fixed period, such as a daily or weekly "
        "cycle; and noise, the random variation that is left. A moving average, the mean of the last few values, "
        "smooths out noise so the trend is easier to see. An autoregressive (AR) model predicts the next value as a "
        "weighted sum of previous values; to capture a daily cycle in hourly data, it can also use the value from 24 "
        "hours earlier. Because the order of the data matters, a time series must not be shuffled before splitting: "
        "the model is trained on the earlier part and tested on the later part, so that it is never tested on the "
        "past using knowledge of the future.",
    ),
    (
        "DAT",
        "Clustering",
        "Clustering is an unsupervised technique that groups data points so that points in the same group (cluster) "
        "are similar and points in different groups are different. The most common algorithm is k-means. First choose "
        "the number of clusters k and pick k starting centres (centroids). Then repeat two steps: assign every point "
        "to its nearest centroid, and move each centroid to the mean of the points assigned to it. Stop when the "
        "assignments no longer change. The value of k is often chosen with the elbow method: plot the total distance "
        "of points to their centroids for several values of k and pick the k where adding more clusters stops giving "
        "a large improvement. Because k-means uses distances, features with large numeric ranges would dominate, so "
        "the features are usually scaled (standardised) first. In IoT, clustering can group households by their "
        "energy-use profiles or sensors by their behaviour, and a reading that is far from every centroid can be "
        "flagged as an anomaly.",
    ),
]
