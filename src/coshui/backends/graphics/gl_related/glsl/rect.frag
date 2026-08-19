#version 330 core

in vec2 vTexCoord;
out vec4 FragColor;

uniform vec4 inColor;
uniform vec2 uSize;
uniform vec4 uRadius;

uniform float uBorderWidth;
uniform vec4 uBorderColor;

float sdRoundedBox(vec2 p, vec2 b, vec4 r)
{
    vec2 select_r = (p.x > 0.0) ? r.yz: r.xw;
    float radius = (p.y < 0.0) ? select_r.x: select_r.y;

    vec2 q = abs(p) - b + vec2(radius);

    return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - radius;
}

void main()
{
    // Convert UVs (0..1) into local pixel coordinates
    vec2 p = (vTexCoord - 0.5) * uSize;

    vec2 outerHalf = uSize * 0.5;

    // Inner shape used to carve out the border
    vec2 innerHalf = max(outerHalf - vec2(uBorderWidth), vec2(0.0));
    vec4 innerRadius = max(uRadius - vec4(uBorderWidth), vec4(0.0));

    float outerDist = sdRoundedBox(p, outerHalf, uRadius);
    float innerDist = sdRoundedBox(p, innerHalf, innerRadius);

    // Anti-aliased masks
    float outerMask = 1.0 - smoothstep(-1.0, 0.0, outerDist);
    float innerMask = 1.0 - smoothstep(-1.0, 0.0, innerDist);

    // Ring between outer and inner shapes
    float borderMask = clamp(outerMask - innerMask, 0.0, 1.0);

    vec3 rgb = inColor.rgb * innerMask + uBorderColor.rgb * borderMask;
    float alpha = inColor.a * innerMask + uBorderColor.a * borderMask;

    FragColor = vec4(rgb, alpha);
}