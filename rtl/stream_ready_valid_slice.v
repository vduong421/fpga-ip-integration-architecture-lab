// Small ready/valid pipeline slice for architecture validation.
// This is intentionally simple RTL that shows hardware-interface thinking.

module stream_ready_valid_slice #(
    parameter DATA_WIDTH = 32
) (
    input  wire                  clk,
    input  wire                  rst_n,
    input  wire                  in_valid,
    output wire                  in_ready,
    input  wire [DATA_WIDTH-1:0] in_data,
    output wire                  out_valid,
    input  wire                  out_ready,
    output wire [DATA_WIDTH-1:0] out_data
);

    reg                  valid_q;
    reg [DATA_WIDTH-1:0] data_q;

    assign in_ready = !valid_q || out_ready;
    assign out_valid = valid_q;
    assign out_data = data_q;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            valid_q <= 1'b0;
            data_q <= {DATA_WIDTH{1'b0}};
        end else if (in_ready) begin
            valid_q <= in_valid;
            if (in_valid) begin
                data_q <= in_data;
            end
        end
    end

endmodule
