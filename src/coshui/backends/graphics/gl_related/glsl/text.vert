#version 330 core

layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aUV;
out vec2 vTexCoord;

uniform mat4 projection;
uniform float uRotation;
uniform vec2 uCenter;

void main() {
    vec2 pos = aPos;
    vTexCoord = aUV;

    if (uRotation != 0.0) {
        pos -= uCenter;
        float rad = -radians(uRotation);
        float cos_a = cos(rad);
        float sin_a = sin(rad);
        float rotated_x = pos.x * cos_a - pos.y * sin_a;
        float rotated_y = pos.x * sin_a + pos.y * cos_a;
        pos = vec2(rotated_x, rotated_y) + uCenter;
    }

    gl_Position = projection * vec4(pos, 0.0, 1.0);
}