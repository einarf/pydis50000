#version 330

#if defined VERTEX_SHADER

in vec3 in_position;
in vec3 in_normal;
in vec2 in_texcoord_0;

uniform mat4 m_proj;
uniform mat4 m_mv;

out vec2 uv;
out vec3 normal;
out vec3 pos;

void main() {
    vec4 p = m_mv * vec4(in_position, 1.0);
	gl_Position = m_proj * p;
    normal = transpose(inverse(mat3(m_mv))) * in_normal;
    uv = in_texcoord_0;
    pos = p.xyz;
}

#elif defined FRAGMENT_SHADER

out vec4 fragColor;

uniform sampler2D texture_day;
uniform sampler2D texture_night;
uniform sampler2D texture_clouds;
// uniform sampler2D texture_specular;
uniform vec3 sun_pos;

in vec2 uv;
in vec3 normal;
in vec3 pos;

void main()
{
    float v = dot(normalize(normal), normalize(sun_pos - pos));
    float m = smoothstep(0.0, 1.0, v * 3);
    vec4 c = mix(
        texture(texture_night, uv),
        texture(texture_day, uv),
        m
    );
    //float specular_val = texture(texture_specular, uv).r;
    // float specular = pow(max(0.0, dot(reflect(normalize(-sun_pos), normalize(normal)), vec3(0.0, 0.0, -1.0))) * specular_val, 100.0);
    //float specular = pow(max(0.0, dot(reflect(-vec3(1, 0, 0), normalize(normal)), normalize(-pos) )) * specular_val, 132.0);

    fragColor = c + texture(texture_clouds, uv) * m;
}

#endif