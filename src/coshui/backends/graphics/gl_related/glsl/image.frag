#version 330 core

in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D uTexture;
uniform float uAlpha;

void main() {
    vec4 tex_color = texture(uTexture, vTexCoord);
    FragColor = vec4(tex_color.rgb, tex_color.a * uAlpha);
}