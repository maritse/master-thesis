import * as tf from '@tensorflow/tfjs-node';
import * as fs from 'node:fs';


const MODEL_LOCATION = "file://model.json"

const model = await tf.loadLayersModel(MODEL_LOCATION);

//console.log(model.summary());
//console.log(model);

const data = fs.readFileSync('/home/vagrant/from-git/master-thesis/server/client_simulator/federated_data_0.d', 'utf8');
console.log(data);