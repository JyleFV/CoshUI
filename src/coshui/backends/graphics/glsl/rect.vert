#version 330 core

uniform mat4 projection;
in vec2 pos;

void main() {
    gl_position = projection * vec4(pos, 0.0, 1.0)
}