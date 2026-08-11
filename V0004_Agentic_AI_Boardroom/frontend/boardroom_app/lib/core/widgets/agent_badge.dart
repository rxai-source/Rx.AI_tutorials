import 'package:flutter/material.dart';

enum AgentRole { director, sme, writer, critic }

class AgentBadge extends StatelessWidget {
  final AgentRole role;
  final double size;
  final double fontSize;

  const AgentBadge({
    super.key,
    required this.role,
    this.size = 24.0,
    this.fontSize = 11.0,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: _getBgColor(),
        shape: BoxShape.circle,
        border: Border.all(color: _getBorderColor(), width: 1),
      ),
      alignment: Alignment.center,
      child: Text(
        _getInitial(),
        style: TextStyle(
          color: _getTextColor(),
          fontSize: fontSize,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  String _getInitial() {
    switch (role) {
      case AgentRole.director: return 'D';
      case AgentRole.sme: return 'T';
      case AgentRole.writer: return 'W';
      case AgentRole.critic: return 'C';
    }
  }

  Color _getBgColor() {
    switch (role) {
      case AgentRole.director: return const Color(0x266366F1); // rgba(99, 102, 241, 0.15)
      case AgentRole.sme: return const Color(0x2610B981);
      case AgentRole.writer: return const Color(0x26A855F7);
      case AgentRole.critic: return const Color(0x26F59E0B);
    }
  }

  Color _getBorderColor() {
    switch (role) {
      case AgentRole.director: return const Color(0x4D6366F1);
      case AgentRole.sme: return const Color(0x4D10B981);
      case AgentRole.writer: return const Color(0x4DA855F7);
      case AgentRole.critic: return const Color(0x4DF59E0B);
    }
  }

  Color _getTextColor() {
    switch (role) {
      case AgentRole.director: return const Color(0xFF818CF8);
      case AgentRole.sme: return const Color(0xFF34D399);
      case AgentRole.writer: return const Color(0xFFC084FC);
      case AgentRole.critic: return const Color(0xFFFBBF24);
    }
  }
}
