# ruff: noqa: ISC004 — dữ liệu đề: chuỗi dài ngắt dòng trong danh sách là cố ý
"""Tự luận khóa 494 — ĐỢT 3 (27/11/2026). Cùng quy ước với essays.py / essays_b2.py: mỗi ý (câu mô tả, điểm, main,
sub); câu mô tả theo hai mẫu "(any one of: …)" / "(both needed: …)"; câu tính toán tách ý CÁCH LÀM và ý KẾT QUẢ.
Ranh giới (Tuấn duyệt 27/11): train/test chỉ ở DA-TL-04; overfitting / dữ liệu không đại diện ở DA-TL-06; chia chuỗi
thời gian không xáo trộn ở DAT-TL-06; "clustering là không giám sát" ở DA, cách k-means chạy ở DAT."""

ESSAY_B3 = {
    "DA": [
        (
            1,
            "easy",
            "Explain why raw IoT sensor readings need to be analysed, and what predictive maintenance and "
            "anomaly detection each achieve.",
            [
                (
                    "Raw readings are of little use until analysed (any one of: huge amounts of data, must be turned into "
                    "information, needed for decisions).",
                    3,
                    [
                        "large amount",
                        "huge amount",
                        "too much data",
                        "little use",
                        "information",
                        "decision",
                        "insight",
                    ],
                    [],
                ),
                (
                    "Predictive maintenance predicts failures before they happen (any one of: repair in time, avoid "
                    "breakdowns).",
                    4,
                    [
                        "before it happen",
                        "before they happen",
                        "before fail",
                        "before failing",
                        "predict failure",
                        "predicts failure",
                        "in time",
                        "avoid breakdown",
                    ],
                    [],
                ),
                (
                    "Anomaly detection finds readings that do not fit the normal pattern (any one of: unusual readings, a "
                    "sudden spike, a sign of a fault or attack).",
                    3,
                    ["unusual", "normal pattern", "abnormal", "spike", "do not fit", "does not fit", "fault", "attack"],
                    [],
                ),
            ],
            "Raw sensor readings arrive in huge amounts and are of little use until they are analysed and turned into "
            "information and decisions. Predictive maintenance predicts machine failures before they happen, so repairs "
            "can be made in time. Anomaly detection finds readings that do not fit the normal pattern, such as a sudden "
            "spike that may mean a fault or an attack.",
        ),
        (
            2,
            "easy",
            "Describe the components of learning from data: what is unknown, what we have, and what the "
            "learning algorithm produces.",
            [
                (
                    "An unknown target function maps inputs to outputs (any one of: target function, true function f, the real "
                    "relationship we cannot see).",
                    3,
                    [
                        "target function",
                        "true function",
                        "unknown function",
                        "real relationship",
                        "maps input",
                        "map input",
                        "not see",
                        "not known",
                        "not know",
                    ],
                    [],
                ),
                (
                    "We have a data set of past examples (any one of: data set, examples of input with output, training "
                    "data).",
                    3,
                    ["data set", "dataset", "example", "examples", "past data", "training data", "sample", "samples"],
                    [],
                ),
                (
                    "The algorithm picks a final hypothesis from a hypothesis set (any one of: chooses the best candidate model, "
                    "the final model approximates the target function).",
                    4,
                    [
                        "hypothesis set",
                        "final hypothesis",
                        "candidate model",
                        "approximate",
                        "close to the target",
                        "best fit",
                        "fits the data best",
                    ],
                    [],
                ),
            ],
            "There is an unknown target function f that maps inputs to outputs. What we have is a data set of past "
            "examples of inputs with their outputs. The learning algorithm searches a hypothesis set of candidate models "
            "and picks the final hypothesis g that fits the data best, so that it approximates f.",
        ),
        (
            3,
            "easy",
            "How do supervised, unsupervised and reinforcement learning differ in the kind of feedback the "
            "learner gets?",
            [
                (
                    "Supervised: every example has the correct answer (any one of: labels, labelled data, known outputs).",
                    4,
                    ["label", "labels", "labelled", "labeled", "correct answer", "known answer", "known output"],
                    ["supervised"],
                ),
                (
                    "Unsupervised: no labels, finds structure by itself (any one of: no labels, groups similar data, finds "
                    "patterns).",
                    3,
                    [
                        "no label",
                        "no labels",
                        "without label",
                        "without labels",
                        "unlabelled",
                        "unlabeled",
                        "structure",
                        "group",
                        "pattern",
                    ],
                    ["unsupervised"],
                ),
                (
                    "Reinforcement: learns from rewards (any one of: reward, learning by trial, feedback on actions).",
                    3,
                    ["reward", "rewards", "trial and error", "feedback"],
                    ["reinforcement"],
                ),
            ],
            "In supervised learning every training example comes with the correct answer, a label. In unsupervised "
            "learning there are no labels, so the algorithm finds structure, such as groups, by itself. In "
            "reinforcement learning the agent learns by trial and error from rewards.",
        ),
        (
            3,
            "easy",
            "Why is the data split into a training set and a test set before building a model?",
            [
                (
                    "The test set checks performance on data the model has not seen (any one of: unseen data, new data, how "
                    "it will work in practice).",
                    5,
                    ["unseen", "new data", "not seen", "never seen", "has not seen", "in practice", "real use"],
                    [],
                ),
                (
                    "So the test set must be kept separate from training (any one of: kept aside, never used to fit the "
                    "model, held out).",
                    5,
                    [
                        "kept aside",
                        "keep aside",
                        "held-out",
                        "not used for training",
                        "never used",
                        "not used to train",
                    ],
                    [],
                ),
            ],
            "The training set is used to fit the model, and the test set checks how well the model works on data it has "
            "not seen, which is how it will be used in practice. For that, the test set must be kept aside and never "
            "used for training.",
        ),
        (
            3,
            "advanced",
            "A factory wants to predict motor failures from vibration sensors. Describe the data-driven "
            "pipeline from raw data to an action: how the data is prepared, which type of learning fits and why, and "
            "what the system does with a prediction.",
            [
                (
                    "Collect past data with labels (any one of: record which motors failed, labelled history).",
                    2,
                    ["label", "labels", "labelled", "labeled", "history", "past failure", "record"],
                    [],
                ),
                (
                    "Clean the data (any one of: handle missing values, remove outliers from faulty sensors).",
                    2,
                    ["missing", "outlier", "outliers", "clean", "faulty reading"],
                    [],
                ),
                (
                    "Compute features (any one of: average vibration, RMS, peak value over a time window).",
                    2,
                    ["feature", "features", "average", "rms", "mean", "peak"],
                    [],
                ),
                (
                    "Type of learning (both needed: supervised classification or a classifier; because the past "
                    "failures are labelled).",
                    2,
                    ["supervised", "classification", "classifier", "classify"],
                    [],
                ),
                (
                    "Action (any one of: raise an alert, schedule maintenance before failure, notify a technician).",
                    2,
                    ["alert", "schedule", "maintenance", "repair", "warn", "notify"],
                    [],
                ),
            ],
            "First collect past vibration data and record which motors failed, so the data are labelled. Clean the data "
            "by handling missing values and removing outliers from faulty sensors. Compute features such as the average "
            "and peak vibration over each minute. Because the past failures are labelled, supervised classification fits. "
            "When the model predicts a failure, the system raises an alert and schedules maintenance before the motor "
            "breaks.",
        ),
        (
            2,
            "advanced",
            "A model that predicts a greenhouse's humidity was trained only on summer data. It works well "
            "in summer but makes large errors in winter. Using the idea of feasibility of learning, explain why, and "
            "suggest how to fix it.",
            [
                (
                    "The training data are not representative of winter (any one of: only summer conditions, the model never "
                    "saw winter).",
                    3,
                    [
                        "not representative",
                        "representative",
                        "only summer",
                        "never saw",
                        "never seen",
                        "different conditions",
                        "does not cover",
                        "not cover",
                    ],
                    [],
                ),
                (
                    "Low error on training data does not guarantee low error on new data (any one of: in-sample vs "
                    "out-of-sample error, generalisation fails).",
                    2,
                    [
                        "in-sample",
                        "out-of-sample",
                        "training error",
                        "generalis",
                        "generaliz",
                        "generalize",
                        "generalise",
                        "not generalize",
                        "not generalise",
                    ],
                    [],
                ),
                (
                    "Fix: collect data from all seasons, then retrain (any one of: whole year of data, add winter data, "
                    "retrain).",
                    3,
                    [
                        "all season",
                        "all seasons",
                        "every season",
                        "whole year",
                        "add winter",
                        "include winter",
                        "collect winter",
                        "retrain",
                        "more data",
                    ],
                    [],
                ),
                (
                    "Check the model on winter test data before using it (any one of: test on winter, validate on new "
                    "conditions).",
                    2,
                    ["test on winter", "winter test", "winter data", "winter reading", "winter readings", "winter"],
                    ["test", "evaluate", "validate", "check"],
                ),
            ],
            "Learning is only feasible when the training data are representative of the situations where the model is "
            "used; this model only saw summer conditions, so winter is not represented. Its low in-sample error does not "
            "guarantee a low out-of-sample error. To fix it, collect data from all seasons and retrain, then check the "
            "model on winter test data before using it.",
        ),
    ],
    "DAT": [
        (
            1,
            "easy",
            "What does linear regression find, and how is the line fitted to the data?",
            [
                (
                    "It finds a straight line relating the input to the output (any one of: a slope with an intercept, "
                    "y = w0 + w1 x, a linear relationship).",
                    5,
                    ["straight line", "line", "slope", "intercept", "w0", "w1"],
                    [],
                ),
                (
                    "The line is fitted by least squares (any one of: minimise the mean squared error, minimise squared "
                    "differences, MSE).",
                    5,
                    [
                        "least squares",
                        "squared error",
                        "squared difference",
                        "mse",
                        "minimise",
                        "minimize",
                        "minimises",
                        "minimizes",
                    ],
                    [],
                ),
            ],
            "Linear regression finds a straight line y = w0 + w1 x that describes how the output changes with the input. "
            "The line is fitted by least squares, choosing the weights that minimise the mean squared error between "
            "the predicted and actual values.",
        ),
        (
            2,
            "easy",
            "Explain the three components that a time series is often described by.",
            [
                (
                    "Trend: a long-term rise or fall (any one of: long-term increase, long-term decrease, overall "
                    "direction).",
                    4,
                    [
                        "long-term",
                        "long term",
                        "increase",
                        "decrease",
                        "overall direction",
                        "rise",
                        "fall",
                    ],
                    ["trend"],
                ),
                (
                    "Seasonality: a pattern that repeats with a fixed period (any one of: daily cycle, weekly cycle, repeating "
                    "pattern).",
                    3,
                    ["repeat", "repeats", "repeating", "cycle", "period", "daily", "weekly"],
                    ["seasonality", "seasonal"],
                ),
                (
                    "Noise: the random variation that is left (any one of: random, irregular, unpredictable).",
                    3,
                    ["random", "irregular", "unpredictable", "remaining", "leftover"],
                    ["noise"],
                ),
            ],
            "The trend is the long-term increase or decrease. Seasonality is a pattern that repeats with a fixed period, "
            "such as a daily cycle. Noise is the random variation that is left over.",
        ),
        (
            3,
            "easy",
            "Describe how the k-means algorithm groups data points once k starting centroids are chosen.",
            [
                (
                    "Assign every point to its nearest centroid (any one of: nearest, closest).",
                    4,
                    ["nearest", "closest", "close", "shortest distance"],
                    [],
                ),
                (
                    "Move each centroid to the mean of its points (any one of: mean, average, update the centroid).",
                    3,
                    ["mean", "average", "update", "move"],
                    ["centroid", "centre", "center"],
                ),
                (
                    "Repeat until the assignments stop changing (any one of: repeat, converge, stable).",
                    3,
                    ["repeat", "converge", "no longer change", "stop changing", "stable", "iterate"],
                    [],
                ),
            ],
            "Each point is assigned to its nearest centroid. Then each centroid is moved to the mean of the points "
            "assigned to it. These two steps are repeated until the assignments no longer change.",
        ),
        (
            3,
            "easy",
            "Why should features usually be scaled before running k-means clustering?",
            [
                (
                    "k-means groups points by distance (any one of: distance, how far apart points are).",
                    5,
                    ["distance", "distances", "far apart"],
                    [],
                ),
                (
                    "Unscaled, the feature with the larger range dominates (any one of: dominate, outweigh, gets more "
                    "weight).",
                    5,
                    [
                        "dominate",
                        "dominates",
                        "outweigh",
                        "more weight",
                        "larger range",
                        "large range",
                        "bigger values",
                        "larger values",
                    ],
                    [],
                ),
            ],
            "k-means groups points by their distance to the centroids. If the features are not scaled, the feature with "
            "the larger numeric range dominates the distances and the other features hardly matter.",
        ),
        (
            1,
            "advanced",
            "A building's daily energy use was modelled from outdoor temperatures between 10 and 35 degC "
            "as E = 2 + 0.5 T, with E in kWh and T in degC. Predict the energy use at 30 degC, showing your method; "
            "explain what the number 0.5 means; and say whether you would trust a prediction for 60 degC.",
            [
                (
                    "Method: substitute T = 30 into the line (any one of: 2 + 0.5 x 30, 0.5 times 30 plus 2).",
                    2,
                    ["0.5 x 30", "0.5 * 30", "0.5 × 30", "0.5 times 30", "2 + 15", "substitute", "plug", "put 30"],
                    [],
                ),
                ("Result: 17 kWh.", 3, ["17", "17.0"], ["kwh", "energy", "predict", "prediction", "use"]),
                (
                    "0.5 is the slope (any one of: energy rises 0.5 kWh per degree, per 1 degC increase).",
                    2,
                    ["per degree", "per degc", "one degree", "1 degc", "0.5 kwh", "slope"],
                    [],
                ),
                (
                    "60 degC is extrapolation, not to be trusted (any one of: outside the 10 to 35 range, beyond the data, the "
                    "line may not stay linear).",
                    3,
                    [
                        "extrapolation",
                        "extrapolate",
                        "outside",
                        "beyond",
                        "not trust",
                        "not reliable",
                        "not stay linear",
                    ],
                    [],
                ),
            ],
            "Substituting T = 30 gives E = 2 + 0.5 x 30 = 17 kWh. The number 0.5 is the slope: the energy use rises by "
            "0.5 kWh per degree. I would not trust a prediction for 60 degC, because it is outside the 10 to 35 degC "
            "range of the data; that is extrapolation, and the relationship may not stay linear.",
        ),
        (
            2,
            "advanced",
            "You must forecast the next hour's temperature in a greenhouse from hourly readings collected "
            "over three months, and the temperature has a clear daily cycle. How would you split the data for training "
            "and testing, which inputs would your model use, and why?",
            [
                (
                    "Split in time order: train on the earlier part, test on the later part.",
                    3,
                    [
                        "earlier",
                        "later",
                        "first",
                        "last",
                        "older",
                        "oldest",
                        "most recent",
                        "newest",
                        "first part",
                        "last part",
                        "time order",
                        "chronological",
                        "chronologically",
                    ],
                    [],
                ),
                (
                    "Why (any one of: do not shuffle, the future must not leak into training, never test on the past using the "
                    "future).",
                    2,
                    ["not shuffle", "no shuffling", "without shuffling", "future", "leak"],
                    [],
                ),
                (
                    "Inputs: previous hours' values (any one of: last few readings, autoregressive, lagged values).",
                    2,
                    ["previous", "past value", "past values", "autoregressive", "lag", "lagged"],
                    [],
                ),
                (
                    "Daily cycle: also the value from 24 hours earlier (any one of: 24-hour lag, same hour yesterday).",
                    3,
                    ["24", "same hour yesterday", "yesterday"],
                    [],
                ),
            ],
            "I would split the data in time order: train on the first two and a half months and test on the later "
            "part, and not shuffle, so the future never leaks into training. The model would be autoregressive, using "
            "the previous few hours' values, plus the value from 24 hours earlier to capture the daily cycle.",
        ),
    ],
}

PROBES_B3 = {
    "DA-TL-01": [
        (
            "đúng, chữ khác",
            "Sensors produce too much data to read by hand, so it must become information. Predictive "
            "maintenance fixes machines before they fail. Anomaly detection spots unusual readings such as a spike.",
            ">=7",
        ),
        ("chỉ tên", "IoT data analysis includes predictive maintenance and anomaly detection.", "<=3"),
    ],
    "DA-TL-02": [
        (
            "đúng, chữ khác",
            "The true function from input to output is unknown. We have a dataset of past examples. The "
            "algorithm chooses the candidate model that fits the data best from its hypothesis set.",
            ">=7",
        ),
        (
            "chỉ nhắc lại đề",
            "Learning has something unknown, something we have, and something the algorithm produces.",
            "<=2",
        ),
    ],
    "DA-TL-03": [
        (
            "đúng, chữ khác",
            "Supervised learning gets labelled examples. Unsupervised learning gets no labels and finds "
            "groups by itself. Reinforcement learning gets rewards for its actions.",
            ">=7",
        ),
        (
            "đảo supervised/unsupervised",
            "Supervised learning gets no labels and finds groups. Unsupervised learning "
            "gets labelled examples. Reinforcement learning gets rewards.",
            "<=4",
        ),
        ("chỉ tên", "The three types are supervised, unsupervised and reinforcement learning.", "<=2"),
    ],
    "DA-TL-04": [
        (
            "đúng, chữ khác",
            "The test data checks how the model does on new data. It is held out and never used to train.",
            ">=7",
        ),
        ("chỉ tên", "We split the data into a training set and a test set.", "<=2"),
        (
            "chép đề (có 'separate')",
            "We separate the data into a training set and a test set before building a model.",
            "<=2",
        ),
    ],
    "DA-TL-05": [
        (
            "đúng, chữ khác",
            "Record which motors broke so the history is labelled. Remove outliers and fill missing "
            "values. Use the RMS vibration as a feature. Train a classifier, a supervised model. Send an alert to the "
            "technician when a failure is predicted.",
            ">=7",
        ),
        ("thiếu quy trình", "Use machine learning on the vibration data to predict failures.", "<=2"),
    ],
    "DA-TL-06": [
        (
            "đúng, chữ khác",
            "The summer data does not cover winter conditions, so it is not representative. Low "
            "training error does not mean the model generalizes. Retrain with a whole year of data and validate it on "
            "winter readings.",
            ">=7",
        ),
        ("chỉ nhắc lại đề", "The model was trained on summer data and is wrong in winter.", "<=2"),
        (
            "ý 4 viết 'test it with winter data' (Tuấn nêu)",
            "It only saw summer, so it is not representative and does not generalize. Retrain with all seasons. Then "
            "test it with winter data.",
            ">=7",
        ),
    ],
    "DAT-TL-01": [
        (
            "đúng, chữ khác",
            "It finds the slope and intercept of a line through the data. The weights minimize the "
            "squared differences between predictions and real values.",
            ">=7",
        ),
        ("chỉ nhắc lại đề", "Linear regression finds a regression for the data.", "<=2"),
    ],
    "DAT-TL-02": [
        (
            "đúng, chữ khác",
            "The trend is the overall direction over a long time. Seasonality is a cycle that repeats, "
            "like every day. Noise is the irregular part that is left over.",
            ">=7",
        ),
        ("chỉ tên", "The three components are trend, seasonality and noise.", "<=2"),
        (
            "đảo trend/seasonality, câu riêng",
            "The trend is a cycle that repeats every day. Seasonality is the long-term rise. Noise is random.",
            "<=4",
        ),
    ],
    "DAT-TL-03": [
        (
            "đúng, chữ khác",
            "Every point joins the closest centroid. Each centroid then moves to the average of its "
            "points. This is repeated until nothing changes and it converges.",
            ">=7",
        ),
        ("chỉ nhắc lại đề", "k-means groups the data points into k groups.", "<=2"),
    ],
    "DAT-TL-04": [
        (
            "đúng, chữ khác",
            "Clustering uses the distance between points. A feature with bigger values would outweigh the others.",
            ">=7",
        ),
        ("chỉ nhắc lại đề", "Features should be scaled before clustering.", "<=2"),
    ],
    "DAT-TL-05": [
        (
            "đúng, chữ khác",
            "Put 30 into the formula: 2 + 0.5 x 30 = 17 kWh of energy. The slope 0.5 means 0.5 kWh more "
            "per degree. 60 degC is beyond the data, so I would not trust it.",
            ">=7",
        ),
        (
            "thay sai số",
            "Using 60 instead: 2 + 0.5 x 60 = 32 kWh of energy. The slope is 0.5. I would trust 60 degC.",
            "<=5",
        ),
        (
            "viết 17.0 kWh, 2 + 15",
            "Substitute T = 30: E = 2 + 15 = 17.0 kWh. 0.5 is the slope. 60 degC is outside the "
            "range, so it is extrapolation.",
            ">=7",
        ),
    ],
    "DAT-TL-06": [
        (
            "đúng, chữ khác",
            "Use the first months for training and the last weeks for testing, without shuffling, so "
            "no future data leaks. Use lagged values of the past hours and the same hour yesterday.",
            ">=7",
        ),
        (
            "xáo trộn ngẫu nhiên",
            "Shuffle the readings randomly and split them 80/20. Use the humidity as the input.",
            "<=3",
        ),
    ],
}

GEMINI_PROBES_B3 = {
    "DA-TL-01": (
        "Raw readings are of little use until analysed. Predictive maintenance predicts failures before they happen. "
        "Anomaly detection finds unusual readings.",
        "Sensors send huge amounts of data that must be turned into decisions. Predictive maintenance lets repairs "
        "happen in time. Anomaly detection finds a sudden spike that may mean an attack.",
    ),
    "DA-TL-02": (
        "The target function is unknown. We have a data set of examples. The algorithm picks a final hypothesis from "
        "the hypothesis set.",
        "We cannot see the true function from inputs to outputs. We have training data. The algorithm chooses the "
        "candidate model that approximates the target.",
    ),
    "DA-TL-03": (
        "Supervised learning has labels. Unsupervised learning has no labels. Reinforcement learning learns from "
        "rewards.",
        "In supervised learning the correct answers are known. Unsupervised learning finds patterns by itself. "
        "Reinforcement learning learns by trial and error.",
    ),
    "DA-TL-04": (
        "The test set shows how the model works on unseen data. It is kept aside during training.",
        "We want to know how the model performs in practice on new data. So the test data is held out and never used "
        "to fit the model.",
    ),
    "DA-TL-05": (
        "Collect labelled history. Clean the data by removing outliers. Compute the average vibration as a feature. "
        "Use supervised learning. Raise an alert.",
        "Record past failures. Handle missing values. Use the peak vibration as a feature. Train a classifier because "
        "the failures are labelled. Schedule maintenance before the motor breaks.",
    ),
    "DA-TL-06": (
        "The summer data is not representative of winter. Low in-sample error does not guarantee low out-of-sample "
        "error. Collect data from all seasons and retrain. Validate on winter data.",
        "The model never saw winter conditions. It does not generalize. Add a whole year of data and retrain, then "
        "test on winter before using it.",
    ),
    "DAT-TL-01": (
        "Linear regression finds a straight line. It is fitted by least squares.",
        "It finds the slope and intercept relating input to output. The weights minimise the mean squared error.",
    ),
    "DAT-TL-02": (
        "Trend: a long-term increase. Seasonality: a repeating daily cycle. Noise: random variation.",
        "Trend is the overall direction. Seasonality is a pattern with a fixed period, like weekly. Noise is the "
        "irregular part left over.",
    ),
    "DAT-TL-03": (
        "Assign every point to its nearest centroid. Move each centroid to the mean of its points. Repeat until "
        "stable.",
        "Each point goes to the closest centre. Each centre is updated to the average of its points. Iterate until "
        "the assignments no longer change.",
    ),
    "DAT-TL-04": (
        "k-means uses distances between points. The feature with the larger range would dominate.",
        "Points are grouped by how far apart they are. Without scaling, a feature with larger values gets more weight.",
    ),
    "DAT-TL-05": (
        "E = 2 + 0.5 x 30 = 17 kWh. 0.5 is the slope, 0.5 kWh per degree. 60 degC is extrapolation, so I would not "
        "trust it.",
        "Substitute T = 30 to predict 17 kWh of energy use. Each 1 degC adds 0.5 kWh. 60 degC is outside the 10 to "
        "35 range, so the line may not stay linear.",
    ),
    "DAT-TL-06": (
        "Train on the earlier part and test on the later part. Do not shuffle, so the future does not leak. Use the "
        "previous hours as inputs. Also use the value 24 hours earlier.",
        "Split chronologically. Never test on the past using the future. Use lagged values of the last few hours. "
        "Add the same hour yesterday to capture the daily cycle.",
    ),
}
