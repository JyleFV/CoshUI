#version 330 core

in vec2 vTexCoord;
out vec4 FragColor;

uniform vec4 inColor;
uniform vec2 uSize;
uniform vec4 uRadius; // (Top-Left, Top-Right, Bottom-Right, Bottom-Left)

// Bulletproof independent corner radius SDF
float sdRoundedBox(vec2 p, vec2 b, vec4 r) {
    // Select the correct radius value based on which quadrant the pixel lies in
    // Top-Left (x <= 0, y >= 0), Top-Right (x > 0, y >= 0)
    // Bottom-Right (x > 0, y < 0), Bottom-Left (x <= 0, y < 0)
    vec2 select_r = (p.x > 0.0) ? r.yz : r.xw;
    float radius  = (p.y > 0.0) ? select_r.x : select_r.y;

    vec2 q = abs(p) - b + vec2(radius);
    return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - radius;
}

void main() {
    vec2 p = (vTexCoord - 0.5) * uSize;

    p.y = -p.y;

    vec2 halfSize = uSize * 0.5;

    float distance = sdRoundedBox(p, halfSize, uRadius);

    float alpha_mask = 1.0 - smoothstep(-1.0, 0.0, distance);

    FragColor = vec4(inColor.rgb, inColor.a * alpha_mask);
}