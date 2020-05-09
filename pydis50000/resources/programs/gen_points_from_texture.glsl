#version 330

#if defined VERTEX_SHADER

void main() {
    float x = gl_VertexID % 512;
    float y = floor(gl_VertexID / 512.0);
    gl_Position = vec4(x, y, 0.0, 1.0);
}

#elif defined GEOMETRY_SHADER

layout(points) in;
layout(points, max_vertices = 1) out;

uniform sampler2D texture0;

out vec3 out_pos;

void main() {
    vec2 pos = gl_in[0].gl_Position.xy;
    vec3 frag = texelFetch(texture0, ivec2(pos), 0).xyz;
    // Parts of the logo we care about
    // 202 214 255
    // 255 255 255
    if (frag == vec3(202.0/255.0, 214.0/255.0, 255.0/255.0) || frag == vec3(1.0, 1.0, 1.0)) {
        out_pos = vec3(pos - vec2(256, 256), -400.0);
        EmitVertex();
        EndPrimitive();
    }

    // out_pos = vec3(pos, 0.0);
    // EmitVertex();
    // EndPrimitive();
    
}

#endif
