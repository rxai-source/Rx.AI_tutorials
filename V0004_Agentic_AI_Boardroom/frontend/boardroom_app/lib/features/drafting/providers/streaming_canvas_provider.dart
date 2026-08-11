import 'package:flutter_riverpod/flutter_riverpod.dart';

final fakeTokens = [
  "Once ", "upon ", "a ", "time, ", "in ", "a ", "world ", "where ",
  "algorithms ", "ruled, ", "there ", "lived ", "a ", "curious ",
  "little ", "data ", "packet ", "named ", "Spark. ", "\n\n",
  "Spark ", "loved ", "to ", "travel ", "through ", "the ", "vast ",
  "neural ", "networks, ", "learning ", "new ", "things ", "every ", "day. ",
  "\n\nOne ", "day, ", "Spark ", "discovered ", "a ", "mysterious ", "glitch..."
];

final streamingCanvasProvider = StreamProvider<String>((ref) async* {
  String currentText = "";
  // Optional initial delay
  await Future.delayed(const Duration(milliseconds: 500));
  
  for (final token in fakeTokens) {
    await Future.delayed(const Duration(milliseconds: 150));
    currentText += token;
    yield currentText;
  }
});
