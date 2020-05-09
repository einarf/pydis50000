#version 330

#if defined VERTEX_SHADER

in vec3 in_pos;

void main() {
    gl_Position = vec4(in_pos, 1.0);
}

#elif defined GEOMETRY_SHADER

layout(points) in;
layout(triangle_strip, max_vertices = 4) out;

uniform mat4 m_mv;
uniform mat4 m_proj;
uniform int num_layers;

out vec3 geo_uv;
out float geo_fade;

void main() {
    const float size = 0.5;
    vec3 pos = gl_in[0].gl_Position.xyz;
    vec3 right = vec3(m_mv[0][0], m_mv[1][0], m_mv[2][0]);
    vec3 up = vec3(m_mv[0][1], m_mv[1][1], m_mv[2][1]);
    int avatar_id = gl_PrimitiveIDIn % num_layers;

    vec4 pos_trans = m_proj * m_mv * vec4(pos, 1.0);
    // float fade = clamp(1.0 - 1.0 / pos_trans.z, 0.0, 1.0);
    // float fade = 1.0 - pos_trans.z / 180.0;
    float fade = 1.0;
    // if (pos_trans.z < 1.0) fade = pos_trans.z;
    // if (pos_trans.z > 2.0) {
    //     fade = pos_trans.z;
    // }

    geo_uv = vec3(1.0, 1.0, avatar_id);
    geo_fade = fade;
    gl_Position = m_proj * m_mv * vec4(pos + (right + up) * size, 1.0);
    EmitVertex();

    geo_uv = vec3(0.0, 1.0, avatar_id);
    geo_fade = fade;
    gl_Position = m_proj * m_mv * vec4(pos + (-right + up) * size, 1.0);
    EmitVertex();

    geo_uv = vec3(1.0, 0.0, avatar_id);
    geo_fade = fade;
    gl_Position = m_proj * m_mv * vec4(pos + (right - up) * size, 1.0);
    EmitVertex();

    geo_uv = vec3(0.0, 0.0, avatar_id);
    geo_fade = fade;
    gl_Position = m_proj * m_mv * vec4(pos + (-right - up) * size, 1.0);
    EmitVertex();

    EndPrimitive();
}

#elif defined FRAGMENT_SHADER

uniform sampler2DArray texture0;
in vec3 geo_uv;
in float geo_fade;
out vec4 fragColor;

void main() {
    float dist = length(geo_uv.xy * 2.0 - vec2(1.0));
    if (dist > 1.0) discard;
    fragColor = vec4(texture(texture0, geo_uv).xyz, geo_fade);
}
#endif
