from vpython import *
import numpy as np

# Physic configuration
degree = 0
n_air = 1.0
n_water = [1.3320, 1.3325, 1.3331, 1.3349, 1.3390, 1.3435]  # red, orange, yellow, green, blue, purple

scene = canvas(
    background=vec(1, 1, 1),
    width=1200,
    height=1000,
    center=vec(0, 0, 0),
    range=10,
    userspin=False,
    userpan=False,
    userzoom=True,
    caption='',
)


# squared perpendicular reflection coefficient
def rs_coefficient(i, t, n1, n2):
    theta_c = asin(min(n2 / n1, 1))
    k = (pi / 2) / theta_c
    return k * (sin(t - i) / sin(t + i)) ** 2


# squared parallel reflection coefficient
def rp_coefficient(i, t, n1, n2):
    theta_c = asin(min(n2 / n1, 1))
    k = (pi / 2) / theta_c
    return k * (tan(t - i) / tan(t + i)) ** 2


class Ray:
    def __init__(self, _pos=vec(0, 0, 0), angle=0):
        self.incidence_y = _pos.y
        _pos = rotate(_pos, -angle)
        self.pos = np.array([], dtype=vec)
        self.v = np.array([], dtype=vec)
        self.axis = []
        self.log = [[], [], [], [], [], []]
        self.opacity = [[], [], [], [], [], []]
        self.exit_angles = []
        self.dt = 0.001

        self.in_lens = [False, False, False, False, False, False]
        self.reflected = [0, 0, 0, 0, 0, 0]

        for i in range(6):
            self.v = np.append(self.v, vec(cos(-angle), sin(-angle), 0))
            self.pos = np.append(self.pos, _pos)

        beam_radius = 0.05
        self.white = cylinder(pos=_pos,
                              color=color.white,
                              radius=beam_radius,
                              axis=vec(0, 0, 0),
                              ball_v=vec(cos(-angle), sin(-angle), 0),
                              ball_pos=_pos,
                              canvas=scene)
        self.beams = [
            [
                cylinder(pos=_pos,
                         color=color.red,
                         radius=beam_radius,
                         visible=False,
                         canvas=scene)
            ],
            [
                cylinder(pos=_pos,
                         color=color.orange,
                         radius=beam_radius,
                         visible=False,
                         canvas=scene)
            ],
            [
                cylinder(pos=_pos,
                         color=color.yellow,
                         radius=beam_radius,
                         visible=False,
                         canvas=scene)
            ],
            [
                cylinder(pos=_pos,
                         color=color.green,
                         radius=beam_radius,
                         visible=False,
                         canvas=scene)
            ],
            [
                cylinder(pos=_pos,
                         color=color.blue,
                         radius=beam_radius,
                         visible=False,
                         canvas=scene)
            ],
            [
                cylinder(pos=_pos,
                         color=color.purple,
                         radius=beam_radius,
                         visible=False,
                         canvas=scene)
            ]]

    def refract(self, droplet_pos, droplet_r):
        for i in range(6):
            if not self.in_lens[i] and self.reflected[i] == 0 and mag(droplet_pos - self.pos[i]) <= droplet_r:
                is_in_type = True
                self.in_lens[i] = True
                self.log[i].append(self.pos[i])
                self.white.ball_v = vec(0, 0, 0)
                self.white.axis = self.white.ball_pos - self.white.pos
            elif self.in_lens[i] and self.reflected[i] >= 1 and mag(
                    droplet_pos - self.pos[i]) >= droplet_r:
                is_in_type = False
                self.in_lens[i] = False
                self.log[i].append(self.pos[i])
                self.beams[i].append(
                    cylinder(pos=self.log[i][1],
                             color=self.beams[i][0].color,
                             radius=self.beams[i][0].radius,
                             axis=self.log[i][2] - self.log[i][1],
                             opacity=self.opacity[i][1] * self.opacity[i][0],
                             canvas=scene))
                self.beams[i].append(
                    cylinder(pos=self.log[i][2],
                             color=self.beams[i][0].color,
                             radius=self.beams[i][0].radius,
                             axis=self.pos[i] - self.log[i][2],
                             canvas=scene))
            else:
                continue
            n1 = n_air if is_in_type else n_water[i]
            n2 = n_air if not is_in_type else n_water[i]
            normal_v = norm(droplet_pos - self.pos[i])
            normal_v *= -1 if not is_in_type else 1
            angle_in = diff_angle(self.v[i], normal_v)
            angle_out = asin(n1 / n2 * sin(angle_in))
            self.opacity[i].append(1 - (rs_coefficient(angle_in, angle_out, n1, n2) +
                                        rp_coefficient(angle_in, angle_out, n1, n2)) / 2)
            self.v[i] = rotate(normal_v,
                               angle=angle_out,
                               axis=cross(normal_v, self.v[i]))
            if not is_in_type and (i == 0 or i == 5) and len(
                    self.beams[i]) == 3:
                self.exit_angles.append(
                    diff_angle(self.v[i], -self.white.axis) * 180 / pi)
            self.pos[i] += self.v[i] * 0.1

    def reflect(self, droplet_pos, droplet_r):
        for i in range(6):
            if self.in_lens[i] and self.reflected[i] == 0 and mag(
                    droplet_pos - self.pos[i]) >= 0.999 * droplet_r:
                self.reflected[i] += 1
                self.log[i].append(self.pos[i])
                self.beams[i][0].pos = self.log[i][0]
                self.beams[i][0].axis = self.log[i][1] - self.log[i][0]
                self.beams[i][0].opacity = self.opacity[i][0]
                self.beams[i][0].visible = True

                normal_v = norm(droplet_pos - self.pos[i])
                n1 = n_water[i]
                n2 = n_air
                angle_in = diff_angle(-self.v[i], normal_v)
                angle_out = asin(n_water[i] / n_air * sin(angle_in))
                self.opacity[i].append((rs_coefficient(angle_in, angle_out, n1, n2) +
                                        rp_coefficient(angle_in, angle_out, n1, n2)) / 2)
                angle_ref = diff_angle(-self.v[i], normal_v)
                self.v[i] = rotate(normal_v,
                                   angle=angle_ref,
                                   axis=cross(normal_v, self.v[i]))
                self.pos[i] += self.v[i] * 0.1

    def update(self, droplet_pos, droplet_r):
        for i in range(6):
            self.refract(droplet_pos, droplet_r)
            self.reflect(droplet_pos, droplet_r)
            if len(self.beams[i]) >= 3:
                self.beams[i][2].axis = self.pos[i] - self.log[i][2]
            if len(self.exit_angles) >= 2:
                if self.beams[i][2].opacity == 1:
                    self.beams[i][2].opacity = self.opacity[i][0] * self.opacity[i][1] * self.opacity[i][2]

        self.pos += self.v * self.dt
        self.white.ball_pos += self.white.ball_v * self.dt


droplet = sphere(radius=5,
                 pos=vec(0, 0, 0),
                 color=vec(82 / 255, 229 / 255, 242 / 255),
                 opacity=0.05,
                 canvas=scene)

ray_arr = []


def run_droplet(f_degree):
    for i in range(16):
        ray_arr.append(Ray(vec(-8, (i + 4) / 4, 0), f_degree))
        done = False
        while not done:
            rate(100000)
            ray_arr[i].update(droplet.pos, droplet.radius)
            for j in range(6):
                if mag(ray_arr[i].pos[j]) >= 15:
                    done = True
                    break


angle_label = wtext(text='', pos=scene.title_anchor)
angle_label.text = "Угол падения: {0:3.1f}".format(degree * 180 / pi) + " градусов"
run_droplet(degree)
