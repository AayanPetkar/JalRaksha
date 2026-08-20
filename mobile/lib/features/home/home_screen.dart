import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('JalRaksha — जलरक्षा'),
        backgroundColor: Colors.blueGrey[900],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: const [
            Icon(Icons.shield, size: 80, color: Colors.blue),
            SizedBox(height: 16),
            Text(
              'Know the Risk. Understand the Impact.',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text('Phase 1 Scaffolding Complete'),
          ],
        ),
      ),
    );
  }
}
