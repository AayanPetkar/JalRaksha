import 'package:flutter/material.dart';
import 'features/home/home_screen.dart';

void main() {
  runApp(const JalRakshaApp());
}

class JalRakshaApp extends StatelessWidget {
  const JalRakshaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'JalRaksha',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
