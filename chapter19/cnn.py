import marimo

__generated_with = "0.13.13-dev18"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    """
    # CNN Kernel Convolution Demonstration

    This notebook demonstrates how a 3x3 kernel convolves with a 4x4 input image 
    to produce a 2x2 activation map in convolutional neural networks.
    """

    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Create sliders for the 3x3 kernel weights
    k00 = mo.ui.slider(-2, 2, 0.1, value=0, label="K[0,0]")
    k01 = mo.ui.slider(-2, 2, 0.1, value=0, label="K[0,1]")
    k02 = mo.ui.slider(-2, 2, 0.1, value=0, label="K[0,2]")
    k10 = mo.ui.slider(-2, 2, 0.1, value=0, label="K[1,0]")
    k11 = mo.ui.slider(-2, 2, 0.1, value=1, label="K[1,1]")
    k12 = mo.ui.slider(-2, 2, 0.1, value=0, label="K[1,2]")
    k20 = mo.ui.slider(-2, 2, 0.1, value=0, label="K[2,0]")
    k21 = mo.ui.slider(-2, 2, 0.1, value=0, label="K[2,1]")
    k22 = mo.ui.slider(-2, 2, 0.1, value=0, label="K[2,2]")

    # Display the sliders in a grid
    mo.md(
        f"""
    ## Kernel Weights (3x3)
    Adjust the kernel weights using the sliders below:

    | | | |
    |---|---|---|
    | {k00} | {k01} | {k02} |
    | {k10} | {k11} | {k12} |
    | {k20} | {k21} | {k22} |
    """
    )
    return k00, k01, k02, k10, k11, k12, k20, k21, k22, mo, np, plt


@app.cell(hide_code=True)
def _(k00, k01, k02, k10, k11, k12, k20, k21, k22, np, plt):
    input_image = np.arange(1, 17, dtype=np.float64).reshape(4, 4)
    kernel = np.array(
        [
            [k00.value, k01.value, k02.value],
            [k10.value, k11.value, k12.value],
            [k20.value, k21.value, k22.value],
        ],
        dtype=np.float64,
    )


    def convolution_2d(image, kernel):
        """
        Perform 2D convolution without padding
        """

        image_height, image_width = image.shape
        kernel_height, kernel_width = kernel.shape

        # Calculate output dimensions
        output_height = image_height - kernel_height + 1
        output_width = image_width - kernel_width + 1

        # Initialize output with explicit dtype
        output = np.zeros((output_height, output_width), dtype=np.float64)

        # Perform convolution
        for i in range(output_height):
            for j in range(output_width):
                # Extract the region of interest
                roi = image[i : i + kernel_height, j : j + kernel_width]
                # Element-wise multiplication and sum
                output[i, j] = np.sum(roi * kernel)
        return output


    activation_map = convolution_2d(input_image, kernel)

    if activation_map is not None:
        print("Activation Map (2x2):")
        print(activation_map)
        print("Activation map dtype:", activation_map.dtype)
    else:
        print("Error: Could not compute activation map")
        activation_map = np.zeros((2, 2), dtype=np.float64)

    # Create simplified visualization - only the first 3 plots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(
        "CNN Convolution Process: 3x3 Kernel on 4x4 Input",
        fontsize=16,
        fontweight="bold",
    )


    # Helper function to add grid and labels
    def setup_heatmap(ax, data, title, annot_fontsize=12):
        # Ensure data is numeric
        data_array = np.asarray(data, dtype=np.float64)
        im = ax.imshow(data_array, cmap="viridis", aspect="equal")
        ax.set_title(title, fontsize=12, fontweight="bold")

        # Add value annotations
        for i in range(data_array.shape[0]):
            for j in range(data_array.shape[1]):
                ax.text(
                    j,
                    i,
                    f"{data_array[i, j]:.1f}",
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=annot_fontsize,
                    fontweight="bold",
                )

        # Add grid
        ax.set_xticks(np.arange(-0.5, data_array.shape[1], 1), minor=True)
        ax.set_yticks(np.arange(-0.5, data_array.shape[0], 1), minor=True)
        ax.grid(which="minor", color="white", linestyle="-", linewidth=2)
        ax.tick_params(which="minor", size=0)
        ax.set_xticks([])
        ax.set_yticks([])


    # Show input image
    setup_heatmap(axes[0], input_image, "Input Image (4×4)")

    # Show kernel
    setup_heatmap(axes[1], kernel, "Kernel (3×3)")

    # Show activation map
    setup_heatmap(axes[2], activation_map, "Activation Map (2×2)")

    plt.tight_layout()
    plt.show()
    return activation_map, kernel


@app.cell(hide_code=True)
def _(activation_map, kernel, mo):
    mo.md(
        f"""
    ## Detailed Calculations

    For each position in the 2×2 output, we calculate the dot product between the 3×3 kernel and the corresponding 3×3 region of the input:

    **Position (0,0) - Top-Left:**
    ```
    Input Region:     Kernel:          Calculation:
    [ 1  2  3]       [{kernel[0,0]:4.1f} {kernel[0,1]:4.1f} {kernel[0,2]:4.1f}]    {1*kernel[0,0]:.1f} + {2*kernel[0,1]:.1f} + {3*kernel[0,2]:.1f} +
    [ 5  6  7]   ×   [{kernel[1,0]:4.1f} {kernel[1,1]:4.1f} {kernel[1,2]:4.1f}] =  {5*kernel[1,0]:.1f} + {6*kernel[1,1]:.1f} + {7*kernel[1,2]:.1f} +
    [ 9 10 11]       [{kernel[2,0]:4.1f} {kernel[2,1]:4.1f} {kernel[2,2]:4.1f}]    {9*kernel[2,0]:.1f} + {10*kernel[2,1]:.1f} + {11*kernel[2,2]:.1f} = {activation_map[0,0]:.1f}
    ```

    **Position (0,1) - Top-Right:**
    ```
    Input Region:     Kernel:          Calculation:
    [ 2  3  4]       [{kernel[0,0]:4.1f} {kernel[0,1]:4.1f} {kernel[0,2]:4.1f}]    {2*kernel[0,0]:.1f} + {3*kernel[0,1]:.1f} + {4*kernel[0,2]:.1f} +
    [ 6  7  8]   ×   [{kernel[1,0]:4.1f} {kernel[1,1]:4.1f} {kernel[1,2]:4.1f}] =  {6*kernel[1,0]:.1f} + {7*kernel[1,1]:.1f} + {8*kernel[1,2]:.1f} +
    [10 11 12]       [{kernel[2,0]:4.1f} {kernel[2,1]:4.1f} {kernel[2,2]:4.1f}]    {10*kernel[2,0]:.1f} + {11*kernel[2,1]:.1f} + {12*kernel[2,2]:.1f} = {activation_map[0,1]:.1f}
    ```

    **Position (1,0) - Bottom-Left:**
    ```
    Input Region:     Kernel:          Calculation:
    [ 5  6  7]       [{kernel[0,0]:4.1f} {kernel[0,1]:4.1f} {kernel[0,2]:4.1f}]    {5*kernel[0,0]:.1f} + {6*kernel[0,1]:.1f} + {7*kernel[0,2]:.1f} +
    [ 9 10 11]   ×   [{kernel[1,0]:4.1f} {kernel[1,1]:4.1f} {kernel[1,2]:4.1f}] =  {9*kernel[1,0]:.1f} + {10*kernel[1,1]:.1f} + {11*kernel[1,2]:.1f} +
    [13 14 15]       [{kernel[2,0]:4.1f} {kernel[2,1]:4.1f} {kernel[2,2]:4.1f}]    {13*kernel[2,0]:.1f} + {14*kernel[2,1]:.1f} + {15*kernel[2,2]:.1f} = {activation_map[1,0]:.1f}
    ```

    **Position (1,1) - Bottom-Right:**
    ```
    Input Region:     Kernel:          Calculation:
    [ 6  7  8]       [{kernel[0,0]:4.1f} {kernel[0,1]:4.1f} {kernel[0,2]:4.1f}]    {6*kernel[0,0]:.1f} + {7*kernel[0,1]:.1f} + {8*kernel[0,2]:.1f} +
    [10 11 12]   ×   [{kernel[1,0]:4.1f} {kernel[1,1]:4.1f} {kernel[1,2]:4.1f}] =  {10*kernel[1,0]:.1f} + {11*kernel[1,1]:.1f} + {12*kernel[1,2]:.1f} +
    [14 15 16]       [{kernel[2,0]:4.1f} {kernel[2,1]:4.1f} {kernel[2,2]:4.1f}]    {14*kernel[2,0]:.1f} + {15*kernel[2,1]:.1f} + {16*kernel[2,2]:.1f} = {activation_map[1,1]:.1f}
    ```

    **Final Activation Map:**
    ```
    [{activation_map[0,0]:6.1f} {activation_map[0,1]:6.1f}]
    [{activation_map[1,0]:6.1f} {activation_map[1,1]:6.1f}]
    ```
    """
    )
    return


if __name__ == "__main__":
    app.run()
