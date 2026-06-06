#version 330 core

layout (location = 0) in vec2 aPos;
out vec2 vTexCoord;

uniform mat4 projection;
uniform float uRotation;
uniform vec2 uCenter;
uniform vec2 uElementPos;
uniform vec2 uSize;

void main() {
    vec2 pos = aPos;

    vTexCoord = (pos - uElementPos) / uSize;

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