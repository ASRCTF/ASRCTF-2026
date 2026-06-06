Neural Oracle - Solution

The first twelve bytes of oracle.bin are a header: four magic bytes followed by
two uint32s (little-endian) giving the offset and size of an embedded TFLite
model. Carve those bytes out and you have a valid .tflite file.

Load it with tf.lite.Interpreter and dump the tensors. The hidden layer has 80
neurons and its bias vector has 80 entries. The first 40 are the negatives of
some target vector x*, and the last 40 are x* itself. The output layer just sums
the hidden activations with a large negative weight and adds a bias of 8. The
whole thing is measuring how far the input is from x*: the closer the input, the
higher the score.

So the flag is sitting right there in the bias. Take the first 40 values, negate
them, multiply each by 255, and round to the nearest integer. Those integers are
the ASCII codes of the flag bytes.

Flag: ASRCTF{4dv3rs4r14l_1nput5_4r3_jus7_m47h}
