import time

def animate_67(lcd, row=0, delay=0.15):
    """
    Animate '6' moving from the left and '7' from the right
    until they meet in the center of the LCD.
    """

    cols = lcd.num_cols

    left_pos = 0
    right_pos = cols - 1

    center_left = (cols // 2) - 1
    center_right = cols // 2

    while left_pos <= center_left and right_pos >= center_right:
        lcd.clear()

        lcd.move_to(left_pos, row)
        lcd.putstr("6")

        lcd.move_to(right_pos, row)
        lcd.putstr("7")

        time.sleep(delay)

        left_pos += 1
        right_pos -= 1

    lcd.clear()
    lcd.move_to(center_left, row)
    lcd.putstr("67")
