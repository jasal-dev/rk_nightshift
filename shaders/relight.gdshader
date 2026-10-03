shader_type canvas_item;
// Relights the detective with the light of the room at the spot he stands on.
//
// TEXTURE   = detective.png        : albedo x ambient occlusion (gamma-encoded), alpha = coverage
// light_tex = detective_light.png  : R/G/B = shading from the left key, right key and top/back rim light
//
// The room's light probes (assets/rooms/<room>_light.json, baked by tools/r3/light_probes.py) give the
// colour of each of those three lights, the ambient, and the fog between the camera and the detective.
// The result is exposed and tone-mapped exactly like the background renders, then gets the same
// vignette and film grain, so he sits in the picture instead of on top of it.

uniform sampler2D light_tex : filter_linear;
uniform vec3 ambient = vec3(0.05);
uniform vec3 key_left = vec3(0.4);
uniform vec3 key_right = vec3(0.4);
uniform vec3 key_rim = vec3(0.2);
uniform vec3 fog_add = vec3(0.0);
uniform float fog_t = 1.0;
uniform float exposure = 1.0;
uniform float grain = 0.012;
uniform bool reflection = false;       // drawn upside down as a wet-street reflection
uniform float reflection_alpha = 0.22;

varying vec2 world_pos;
varying float local_y;
varying vec4 tint;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
	local_y = VERTEX.y;
	tint = COLOR;
}

vec3 aces(vec3 x) {
	return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0);
}

float hash(vec2 p) {
	p = fract(p * vec2(123.34, 456.21));
	p += dot(p, p + 45.32);
	return fract(p.x * p.y);
}

void fragment() {
	vec2 uv = UV;
	if (reflection) {
		// rain-rippled: wobble sideways, more the further from the feet
		float wob = sin(world_pos.y * 0.21 + TIME * 3.0) + 0.5 * sin(world_pos.y * 0.57 - TIME * 4.3);
		uv.x += wob * 0.00045 * clamp(-local_y / 120.0, 0.2, 1.0);
	}
	vec4 alb = texture(TEXTURE, uv);
	vec3 a = pow(alb.rgb, vec3(2.2));
	vec3 s = pow(texture(light_tex, uv).rgb, vec3(2.2));
	vec3 lin = a * (ambient + key_left * s.r + key_right * s.g + key_rim * s.b);
	lin = lin * fog_t + fog_add;
	vec3 c = pow(aces(lin * exposure), vec3(1.0 / 2.2));
	// same finish as the background: soft vignette and fine grain
	vec2 r2 = (world_pos - vec2(960.0, 540.0)) / vec2(960.0, 540.0);
	float r = length(r2);
	c *= 1.0 - 0.28 * pow(clamp(r - 0.45, 0.0, 1.0), 1.6);
	float n = hash(floor(world_pos));   // static, like the background's grain (animated grain flickers)
	c += (n - 0.5) * grain * 3.4;
	float alpha = alb.a * tint.a;
	if (reflection) {
		alpha *= reflection_alpha * (1.0 - clamp(-local_y / 300.0, 0.0, 1.0));
		c *= 0.8;
	}
	COLOR = vec4(c * tint.rgb, alpha);
}
