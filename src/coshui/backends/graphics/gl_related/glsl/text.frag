#version 330 core

in vec2 vTexCoord;
out vec4 FragColor;

uniform sampler2D uAtlas;
uniform vec4 uTextColor;

void main() {
    float alpha = texture(uAtlas, vTexCoord).r;
    FragColor = vec4(uTextColor.rgb, uTextColor.a * alpha);
}