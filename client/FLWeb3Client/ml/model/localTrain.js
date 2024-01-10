import * as tf from "@tensorflow/tfjs";
import "@tensorflow/tfjs-react-native";

async function loadData(data) {
  const data = await tf.data.csv(data);
  const featureColumns = data.columnNames().slice(1);
  const labelColumn = data.columnNames()[0];

  const features = data
    .map((row) => tf.tensor(Object.values(row.xs), [28, 28, 1]))
    .toArray();

  const labels = data
    .map((row) => tf.oneHot(row.ys[labelColumn], 10))
    .toArray();

  return { features, labels };
}

function createModel() {
  const model = tf.sequential();
  model.add(tf.layers.flatten({ inputShape: [28, 28, 1] }));
  model.add(tf.layers.dense({ units: 128, activation: "relu" }));
  model.add(tf.layers.dense({ units: 10, activation: "softmax" }));

  model.compile({
    optimizer: tf.train.adam(),
    loss: "categoricalCrossentropy",
    metrics: ["accuracy"],
  });

  return model;
}

async function trainModel(model, features, labels) {
  const xs = tf.stack(features);
  const ys = tf.stack(labels);

  await model.fit(xs, ys, {
    epochs: 10,
    shuffle: true,
    validationSplit: 0.2,
    callbacks: {
      onEpochEnd: (epoch, logs) => {
        console.log(`Epoch ${epoch + 1}, Loss: ${logs.loss}`);
      },
    },
  });
}

async function lostFunction(model, features, labels) {
    const model = createModel();

    const trainFeatures = features.slice(0, 50000);
    const trainLabels = labels.slice(0, 50000);

    const testFeatures = features.slice(50000);
    const testLabels = labels.slice(50000);
  
    await trainModel(model, trainFeatures, trainLabels);
  
    const evalResult = model.evaluate(
        tf.stack(testFeatures),
         tf.stack(testLabels)
    );

    return ${evalResult[1].dataSync()[0]}
}
