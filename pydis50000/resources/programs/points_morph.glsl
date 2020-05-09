#version 330

#if defined VERTEX_SHADER

in vec3 in_pos;
in vec3 in_dest;
in vec3 in_color;

out vec3 vs_dest;
out vec3 vs_color;

void main() {
    gl_Position = vec4(in_pos, 1.0);
    vs_dest = in_dest;
    vs_color = in_color;
}

#elif defined GEOMETRY_SHADER

layout(points) in;
layout(triangle_strip, max_vertices = 4) out;

uniform mat4 m_mv;
uniform mat4 m_proj;
uniform int num_layers;
uniform float interpolate;

in vec3 vs_dest[];
in vec3 vs_color[];

out vec3 geo_uv;
out float geo_fade;
out vec3 geo_color;

void main() {
    const float size = 0.75;
    vec3 pos1 = gl_in[0].gl_Position.xyz;
    vec3 pos2 = vs_dest[0];
    vec3 pos = pos1 + (pos2 - pos1) * interpolate;

    vec3 right = vec3(m_mv[0][0], m_mv[1][0], m_mv[2][0]);
    vec3 up = vec3(m_mv[0][1], m_mv[1][1], m_mv[2][1]);
    int avatar_id = gl_PrimitiveIDIn % num_layers;

    // Control how each point is rendered based on the distanc deom the camera
    vec4 pos_trans = m_proj * m_mv * vec4(pos, 1.0);
    float fade = clamp((pos_trans.z - 100.0) / 100.0, 0.0, 1.0);
    // float fade = 1.0;

    geo_uv = vec3(1.0, 1.0, avatar_id);
    geo_fade = fade;
    geo_color = vs_color[0];
    gl_Position = m_proj * m_mv * vec4(pos + (right + up) * size, 1.0);
    EmitVertex();

    geo_uv = vec3(0.0, 1.0, avatar_id);
    geo_fade = fade;
    geo_color = vs_color[0];
    gl_Position = m_proj * m_mv * vec4(pos + (-right + up) * size, 1.0);
    EmitVertex();

    geo_uv = vec3(1.0, 0.0, avatar_id);
    geo_fade = fade;
    geo_color = vs_color[0];
    gl_Position = m_proj * m_mv * vec4(pos + (right - up) * size, 1.0);
    EmitVertex();

    geo_uv = vec3(0.0, 0.0, avatar_id);
    geo_fade = fade;
    geo_color = vs_color[0];
    gl_Position = m_proj * m_mv * vec4(pos + (-right - up) * size, 1.0);
    EmitVertex();

    EndPrimitive();
}

#elif defined FRAGMENT_SHADER

uniform sampler2DArray texture0;
in vec3 geo_uv;
in float geo_fade;
in vec3 geo_color;

out vec4 fragColor;

void main() {
    float dist = length(geo_uv.xy * 2.0 - vec2(1.0));
    if (dist > 1.0) discard;
    vec4 frag = vec4(texture(texture0, geo_uv).xyz, 1.0);
    // Interpolate between texture and color
    fragColor = vec4(frag.xyz, 1.0) * (1.0 - geo_fade) + vec4(geo_color, 1.0) * geo_fade;
}
#endif
