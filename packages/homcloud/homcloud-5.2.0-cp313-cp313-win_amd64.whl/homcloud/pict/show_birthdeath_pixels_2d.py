from PIL import Image, ImageFont, ImageDraw


def create_base_output_image(original_image, no_label):
    width, height = original_image.size
    if not no_label:
        width += 100
        height += 20

    output_image = Image.new("RGB", (width, height))
    output_image.paste(original_image, (0, 0))
    return output_image


def resize_image(image, scale):
    width, height = image.size
    return image.resize((width * scale, height * scale))


def setup_images(picture, scale, no_label):
    input_image = resize_image(picture, scale)
    output_image = create_base_output_image(input_image, no_label)
    marker_drawer = MarkerDrawer(ImageDraw.Draw(output_image))
    return output_image, marker_drawer


class Pair:
    def __init__(self, birth, death, birth_pos, death_pos):
        self.birth = birth
        self.death = death
        self.birth_pos = birth_pos
        self.death_pos = death_pos

    @property
    def lifetime(self):
        return self.death - self.birth

    def display_str(self):
        return "({0}, {1}) - ({2}, {3}) ({4}, {5})".format(
            self.birth, self.death, self.birth_pos[0], self.birth_pos[1], self.death_pos[0], self.death_pos[1]
        )

    def __repr__(self):
        return "Pair({})".format(self.display_str())


class MarkerDrawer:
    def __init__(self, draw):
        """Marker Drawer

        Args:
        draw -- PIL.ImageDraw.Draw object
        args -- the return value of argument_parser().parse_args()
        """
        self.draw = draw
        self.font = ImageFont.load_default()
        self.scale = 1
        self.marker_type = "filled-diamond"
        self.marker_size = 1
        self.should_draw_birth_pixel = False
        self.should_draw_death_pixel = False
        self.should_draw_line = False
        self.no_label = True
        self.birth_color = (255, 0, 0)
        self.death_color = (0, 0, 255)
        self.line_color = (0, 255, 0)

    def setup_by_args(self, args):
        self.scale = args.scale
        self.marker_size = args.marker_size
        self.marker_type = args.marker_type
        self.should_draw_birth_pixel = args.birth
        self.should_draw_death_pixel = args.death
        self.should_draw_line = args.line
        self.no_label = args.no_label
        self.birth_color = args.birth_color
        self.death_color = args.death_color
        self.line_color = args.line_color
        return self

    def put_label(self, pos, pair, color):
        if self.no_label:
            return
        self.draw.text(scaling(pos, self.scale), "({}, {})".format(pair.birth, pair.death), font=self.font, fill=color)

    def put_birth_marker(self, pair):
        self.put_marker(pair.birth_pos, self.birth_color)
        self.put_label(pair.birth_pos, pair, self.birth_color)

    def put_death_marker(self, pair):
        self.put_marker(pair.death_pos, self.death_color)
        self.put_label(pair.death_pos, pair, self.death_color)

    def draw_pair(self, pair):
        if self.should_draw_line:
            self.put_line(pair)
        if self.should_draw_birth_pixel:
            self.put_birth_marker(pair)
        if self.should_draw_death_pixel:
            self.put_death_marker(pair)

    def put_line(self, pair):
        """Put a line from the birth pixel to the death pixel of the given pair.

        Put a red marker at the birth pixel.
        Put a blue marker at the death pixel.
        Put a green line between them.

        Args:
        pair -- Pair object
        """
        self.draw.line(
            [scaling(pair.birth_pos, self.scale), scaling(pair.death_pos, self.scale)], fill=self.line_color, width=1
        )
        self.put_marker(pair.birth_pos, self.birth_color)
        self.put_marker(pair.death_pos, self.death_color)

    def put_marker(self, pos, color):
        x, y = scaling(pos, self.scale)

        def bounding_box():
            return [x - self.marker_size, y - self.marker_size, x + self.marker_size, y + self.marker_size]

        def put_point():
            self.draw.point((x, y), fill=color)

        def put_filled_diamond():
            for dx in range(-self.marker_size, self.marker_size + 1):
                for dy in range(-self.marker_size, self.marker_size + 1):
                    if abs(dx) + abs(dy) > self.marker_size:
                        continue
                    self.draw.point((x + dx, y + dy), fill=color)

        def put_circle():
            self.draw.ellipse(bounding_box(), outline=color)

        def put_filled_circle():
            self.draw.ellipse(bounding_box(), outline=color, fill=color)

        def put_square():
            self.draw.rectangle(bounding_box(), outline=color)

        def put_filled_square():
            self.draw.rectangle(bounding_box(), outline=color, fill=color)

        if self.marker_type == "filled-diamond":
            put_filled_diamond()
        elif self.marker_type == "point":
            put_point()
        elif self.marker_type == "circle":
            put_circle()
        elif self.marker_type == "filled-circle":
            put_filled_circle()
        elif self.marker_type == "square":
            put_square()
        elif self.marker_type == "filled-square":
            put_filled_square()
        else:
            raise RuntimeError("Unknown marker type: {}".format(self.marker_type))


def scaling(pos, scale):
    x = pos[1] * scale + scale // 2
    y = pos[0] * scale + scale // 2
    return (x, y)
