/********************
* Filename:     bfm_arbiter.v
* Description:  Bus functional model to check the functionality of Arbiter which decides which of the Input port buffer gets the highest priority among the others. Arbitration is based on Round-Robin Scheduling policy with the last served as least priority. Priority direction Local, North, East, South, West
*
* $Revision: 26 $
* $Id: bfm_arbiter.v 26 2015-11-22 19:24:28Z ranga $
* $Date: 2015-11-22 21:24:28 +0200 (Sun, 22 Nov 2015) $
* $Author: ranga $
*********************/
`include "../DUTs/parameters.v"
`include "../DUTs/state_defines.v"

module bfm_arbiter(bfm_clk, bfm_command, bfm_grant);

  input bfm_clk;
  input [5:0] bfm_command;
  
  output reg bfm_grant;
  
  // Declaring the port variables for DUT
  wire        clk;
  
  reg         rst;
  reg [2:0]   Lflit_id, Nflit_id, Eflit_id, Wflit_id, Sflit_id;
  reg [11:0]  Llength, Nlength, Elength, Wlength, Slength;
  reg         Lreq, Nreq, Ereq, Wreq, Sreq;
  
  wire [5:0] nextstate;
  
  // Specifying timeout period
  parameter TIMEOUT = 5;
  integer loop;
  
  always @(negedge clk) begin
    if(!rst) begin
      {Lflit_id, Nflit_id, Eflit_id, Wflit_id, Sflit_id} = {`HEADER, `HEADER, `HEADER, `HEADER, `HEADER};
      Llength = TIMEOUT;
      Nlength = TIMEOUT;
      Elength = TIMEOUT;
      Wlength = TIMEOUT;
      Slength = TIMEOUT;
      for(loop = 0; loop < TIMEOUT-1; loop = loop + 1) begin
        @(negedge clk) begin
          {Lflit_id, Nflit_id, Eflit_id, Wflit_id, Sflit_id} = {`PAYLOAD, `PAYLOAD, `PAYLOAD, `PAYLOAD, `PAYLOAD};
        end
      end
      {Lflit_id, Nflit_id, Eflit_id, Wflit_id, Sflit_id} = {`TAIL, `TAIL, `TAIL, `TAIL, `TAIL};
    end
  end
  
  // Specifying the single pulse request parameter
  parameter NR = 3'b000,        // No request
            RS = 3'b001,        // Request to south
            RW = 3'b010,        // Request to west
            RE = 3'b011,        // Request to east
            RN = 3'b100,        // Request to north
            RL = 3'b101;        // Request to local
            
  // Specifying the continuous pulse(with access time) request parameter
  // Adding Extra bit for FSM Transition. To differentiate L-->N(00001), N-->L(10001). MSB stands for forward/backward
  parameter NRQ   = 6'b00000,           // No request
            RLN   = 6'b00001,           // Local to north
            RLE   = 6'b00010,           // Local to east
            RLW   = 6'b00011,           // Local to west
            RLS   = 6'b00100,           // Local to south
            RLL   = 6'b00101,           // Local to local
            RNE   = 6'b00110,           // North to east
            RNW   = 6'b00111,           // North to west
            RNS   = 6'b01000,           // North to south
            RNL   = 6'b10001,           // North to local
            RNN   = 6'b01001,           // North to north
            REW   = 6'b01010,           // East to west
            RES   = 6'b01011,           // East to south
            REL   = 6'b10010,           // East to local
            REN   = 6'b10110,           // East to north
            REE   = 6'b01100,           // East to east
            RWS   = 6'b01101,           // West to south
            RWL   = 6'b10011,           // West to local
            RWN   = 6'b10111,           // West to north
            RWE   = 6'b11010,           // West to east
            RWW   = 6'b01110,           // West to west
            RSL   = 6'b10100,           // South to local
            RSN   = 6'b11000,           // South to north
            RSE   = 6'b11011,           // South to east
            RSW   = 6'b11101,           // South to west
            RSS   = 6'b01111,           // South to south
            RNE_L = 6'b010000,          // North and East to Local 
            RNW_L = 6'b010001,          // North and West to Local 
            RNS_L = 6'b010010,          // North and South to Local 
            REW_L = 6'b010011,          // East and West to Local 
            RES_L = 6'b010100,          // East and South to Local 
            RWS_L = 6'b010101,          // West and South to Local 
            RLE_N = 6'b010110,          // Local and East to North
            RLW_N = 6'b010111,          // Local and West to North
            RLS_N = 6'b011000,          // Local and South to North
            REW_N = 6'b011001,          // East and West to North
            RES_N = 6'b011010,          // East and South to North
            RWS_N = 6'b011011,          // West and South to North
            RLN_E = 6'b011100,          // Local and North to East
            RLW_E = 6'b011101,          // Local and West to East
            RLS_E = 6'b011110,          // Local and South to East
            RNW_E = 6'b011111,          // North and West to East
            RNS_E = 6'b100000,          // North and South to East
            RWS_E = 6'b100001,          // West and South to East
            RLN_W = 6'b100010,          // Local and North to West
            RLE_W = 6'b100011,          // Local and East to West
            RLS_W = 6'b100100,          // Local and South to West
            RNE_W = 6'b100101,          // North and East to West
            RNS_W = 6'b100110,          // North and South to West
            RES_W = 6'b100111,          // East and South to West
            RLN_S = 6'b101000,          // Local and North to South
            RLE_S = 6'b101001,          // Local and East to South
            RLW_S = 6'b101010,          // Local and West to South
            RNE_S = 6'b101011,          // North and East to South
            RNW_S = 6'b101100,          // North and West to South
            REW_S = 6'b101101;          // East and West to South          
  
  // BFM commands Declaration
  parameter NOREQ1 = 6'd1,
            REQFL  = 6'd2,
            REQFN  = 6'd3,
            REQFE  = 6'd4,
            REQFW  = 6'd5,
            REQFS  = 6'd6,
            NOREQ2 = 6'd7,
            REQFLN = 6'd8,
            REQFLE = 6'd9,
            REQFLW = 6'd10,
            REQFLS = 6'd11,
            REQFLL = 6'd12,
            REQFNE = 6'd13,
            REQFNW = 6'd14,
            REQFNS = 6'd15,
            REQFNL = 6'd16,
            REQFNN = 6'd17,
            REQFEW = 6'd18,
            REQFES = 6'd19,
            REQFEL = 6'd20,
            REQFEN = 6'd21,
            REQFEE = 6'd22,
            REQFWS = 6'd23,
            REQFWL = 6'd24,
            REQFWN = 6'd25,
            REQFWE = 6'd26,
            REQFWW = 6'd27,
            REQFSL = 6'd28,
            REQFSN = 6'd29,
            REQFSE = 6'd30,
            REQFSW = 6'd31,
            REQFSS = 6'd32, 
            REQFNE_L = 6'd33, 
            REQFNW_L = 6'd34, 
            REQFNS_L = 6'd35, 
            REQFEW_L = 6'd36, 
            REQFES_L = 6'd37, 
            REQFWS_L = 6'd38,   
            REQFLE_N = 6'd39,
            REQFLW_N = 6'd40,
            REQFLS_N = 6'd41,
            REQFEW_N = 6'd42,
            REQFES_N = 6'd43,
            REQFWS_N = 6'd44,
            REQFLN_E = 6'd45,
            REQFLW_E = 6'd46,
            REQFLS_E = 6'd47,
            REQFNW_E = 6'd48,
            REQFNS_E = 6'd49,
            REQFWS_E = 6'd50,
            REQFLN_W = 6'd51,
            REQFLE_W = 6'd52,
            REQFLS_W = 6'd53,
            REQFNE_W = 6'd54,
            REQFNS_W = 6'd55,
            REQFES_W = 6'd56,
            REQFLN_S = 6'd57, 
            REQFLE_S = 6'd58, 
            REQFLW_S = 6'd59, 
            REQFNE_S = 6'd60, 
            REQFNW_S = 6'd61, 
            REQFEW_S = 6'd62;  

  assign clk = bfm_clk;
  
  // Instantiate ARBITER DUT              
  arbiter DUT (clk, rst,
                Lflit_id, Nflit_id, Eflit_id, Wflit_id, Sflit_id,
                Llength, Nlength, Elength, Wlength, Slength,
                Lreq, Nreq, Ereq, Wreq, Sreq,
                nextstate
              );
              
  // Task to generate reset
  task reset;
    begin
      rst                                                 = 1;
      {Lflit_id, Nflit_id, Eflit_id, Wflit_id, Sflit_id}  = 0;
      {Llength, Nlength, Elength, Wlength, Slength}       = 0;
      {Lreq, Nreq, Ereq, Wreq, Sreq}                      = 0;
      @(negedge clk);
        if(nextstate != `IDLE) begin
          $display("Reset is not working\n");
          $display("Error at time %0t", $time);
          $stop; 
        end
        $display("TIME:%0t Reset is working\n", $time);
        repeat(2)
          @(negedge clk);
        rst = 0;
    end
  endtask
  
  // Task to request buffer for first time -- single pulse
  task request1;
    input [2:0] data;
    begin
      @(negedge clk) begin
        if(data == 0) begin
          {Lreq, Nreq, Ereq, Wreq, Sreq} = 0;
        end
        else begin
          {Lreq, Nreq, Ereq, Wreq, Sreq} = (1 << (data-1)); // To assert the particular bit since data == 0 is used for IDLE
        end
      end
    end
  endtask
  
  // Task to request buffer for first time withoout last request -- continuous pulse requested by any buffer
  task request2;
    input Lr, Nr, Er, Wr, Sr;
    input [4:0] data;
    begin
      @(negedge clk) begin
        if(data == 0) begin
          {Lreq, Nreq, Ereq, Wreq, Sreq} = 0;
        end
        else begin
          {Lreq, Nreq, Ereq, Wreq, Sreq} = {Lr, Nr, Er, Wr, Sr};
        end
      end
      
      repeat(TIMEOUT+2) //Repeating the request for a particular buffer till timeout occurs followed by round robin priority request
        @(negedge clk);
    end
  endtask
  
  // Sampling and executing Commands
  always @(posedge clk) begin
    case(bfm_command)
      NOREQ1 :
        begin
          bfm_grant = 1'b0;
          request1(NR);
          bfm_grant = 1'b1;
        end
      REQFL :
        begin
          bfm_grant = 1'b0;
          request1(RL);
          request1(NR);
          bfm_grant = 1'b1;
        end
      REQFN :
        begin
          bfm_grant = 1'b0;
          request1(RN);
          request1(NR);
          bfm_grant = 1'b1;
        end
      REQFE :
        begin
          bfm_grant = 1'b0;
          request1(RE);
          request1(NR);
          bfm_grant = 1'b1;
        end
      REQFW :
        begin
          bfm_grant = 1'b0;
          request1(RW);
          request1(NR);
          bfm_grant = 1'b1;
        end
      REQFS :
        begin
          bfm_grant = 1'b0;
          request1(RS);
          request1(NR);
          bfm_grant = 1'b1;
        end
      NOREQ2 :
        begin
          bfm_grant = 1'b0;
          request2(0, 0, 0, 0, 0, NRQ);
          bfm_grant = 1'b1;
        end
      REQFLN :
        begin
          bfm_grant = 1'b0;
          request2(1, 1, 1, 1, 1, RLN);
          bfm_grant = 1'b1;
        end
      REQFLE :
        begin
          bfm_grant = 1'b0;
          request2(1, 0, 1, 1, 1, RLE);
          bfm_grant = 1'b1;
        end
      REQFLW :
        begin
          bfm_grant = 1'b0;
          request2(0, 0, 0, 1, 0, RLW);
          bfm_grant = 1'b1;
        end
      REQFLS :
        begin
          bfm_grant = 1'b0;
          request2(1, 0, 0, 0, 1, RLS);
          bfm_grant = 1'b1;
        end
      REQFLL :
        begin
          bfm_grant = 1'b0;
          request2(1, 0, 0, 0, 0, RLL);
          bfm_grant = 1'b1;
        end
      REQFNE :
        begin
          bfm_grant = 1'b0;
          request2(1, 1, 1, 1, 1, RNE);
          bfm_grant = 1'b1;
        end
      REQFNW :
        begin
          bfm_grant = 1'b0;
          request2(1, 1, 0, 1, 1, RNW);
          bfm_grant = 1'b1;
        end
      REQFNS :
        begin
          bfm_grant = 1'b0;
          request2(1, 1, 0, 0, 1, RNS);
          bfm_grant = 1'b1;
        end
      REQFNL :
        begin
          bfm_grant = 1'b0;
          request2(1, 0, 0, 0, 0, RNL);
          bfm_grant = 1'b1;
        end
      REQFNN :
        begin
          bfm_grant = 1'b0;
          request2(0, 1, 0, 0, 0, RNN);
          bfm_grant = 1'b1;
        end
      REQFEW :
        begin
          bfm_grant = 1'b0;
          request2(1, 1, 1, 1, 1, REW);
          bfm_grant = 1'b1;
        end
      REQFES :
        begin
          bfm_grant = 1'b0;
          request2(1, 1, 1, 0, 1, RES);
          bfm_grant = 1'b1;
        end
      REQFEL :
        begin
          bfm_grant = 1'b0;
          request2(1, 1, 1, 0, 0, REL);
          bfm_grant = 1'b1;
        end
      REQFEN :
        begin
          bfm_grant = 1'b0;
          request2(0, 1, 1, 0, 0, REN);
          bfm_grant = 1'b1;
        end
      REQFEE :
        begin
          bfm_grant = 1'b0;
          request2(0, 0, 1, 0, 0, REE);
          bfm_grant = 1'b1;
        end
      REQFWS :
        begin
          bfm_grant = 1'b0;
          request2(1, 1, 1, 1, 1, RWS);
          bfm_grant = 1'b1;
        end
      REQFWL :
        begin
          bfm_grant = 1'b0;
          request2(1, 1, 1, 1, 0, RWL);
          bfm_grant = 1'b1;
        end
      REQFWN :
        begin
          bfm_grant = 1'b0;
          request2(0, 1, 1, 1, 0, RWN);
          bfm_grant = 1'b1;
        end
      REQFWE :
        begin
          bfm_grant = 1'b0;
          request2(0, 0, 1, 1, 0, RWE);
          bfm_grant = 1'b1;
        end
      REQFWW :
        begin
          bfm_grant = 1'b0;
          request2(0, 0, 0, 1, 0, RWW);
          bfm_grant = 1'b1;
        end
      REQFSL :
        begin
          bfm_grant = 1'b0;
          request2(1, 0, 0, 0, 0, RSL);
          bfm_grant = 1'b1;
        end
      REQFSN :
        begin
          bfm_grant = 1'b0;
          request2(0, 1, 0, 0, 0, RSN);
          bfm_grant = 1'b1;
        end
      REQFSE :
        begin
          bfm_grant = 1'b0;
          request2(0, 0, 1, 0, 0, RSE);
          bfm_grant = 1'b1;
        end
      REQFSW :
        begin
          bfm_grant = 1'b0;
          request2(0, 0, 0, 1, 0, RSW);
          bfm_grant = 1'b1;
        end
      REQFSS :
        begin
          bfm_grant = 1'b0;
          request2(0, 0, 0, 0, 1, RSS);
          bfm_grant = 1'b1;
        end

      // Two requests to Local
      REQFNE_L :
        begin
          bfm_grant = 1'b0;
          request2(0, 1, 1, 0, 0, RNE_L);
          bfm_grant = 1'b1;
        end

      REQFNW_L :
        begin
          bfm_grant = 1'b0;
          request2(0, 1, 0, 1, 0, RNW_L);
          bfm_grant = 1'b1;
        end

      REQFNS_L :
        begin
          bfm_grant = 1'b0;
          request2(0, 1, 0, 0, 1, RNS_L);
          bfm_grant = 1'b1;
        end

      REQFEW_L :
        begin
          bfm_grant = 1'b0;
          request2(0, 0, 1, 1, 0, REW_L);
          bfm_grant = 1'b1;
        end

      REQFES_L :
        begin
          bfm_grant = 1'b0;
          request2(0, 0, 1, 0, 1, RES_L);
          bfm_grant = 1'b1;
        end

      REQFWS_L :
        begin
          bfm_grant = 1'b0;
          request2(0, 0, 0, 1, 1, RWS_L);
          bfm_grant = 1'b1;
        end
        
    endcase
  end

// Properties

property property_0; 
@(negedge clk) 
    (rst) |-> nextstate[0]; 
endproperty

property property_1; 
@(negedge clk) 
    (!Lreq && !Nreq && !Ereq && !Wreq && !Sreq) |-> nextstate[0]; 
endproperty

property property_2; 
@(negedge clk) 
    (!rst && Lflit_id[2] && Lreq && !Nreq && !Ereq && !Wreq && !Sreq) |-> !nextstate[0]; 
endproperty

property property_3; 
@(negedge clk) 
    (!rst && Lflit_id[2] && Sreq) |-> !nextstate[0]; 
endproperty

property property_4; 
@(negedge clk) 
    (!rst && !Lflit_id[2] && !Lflit_id[1] && !Nflit_id[2] && !Eflit_id[2] && !Wflit_id[2] && !Sflit_id[2] && Sreq) |-> !nextstate[0]; 
endproperty

property property_5; 
@(negedge clk) 
    (!rst && Lflit_id[0] && !Lreq && !Nreq && Ereq && !Sreq) |-> !nextstate[0]; 
endproperty

property property_6; 
@(negedge clk) 
    (!rst && Lflit_id[0] && !Lreq && !Nreq && !Ereq && Wreq && !Sreq) |-> !nextstate[0]; 
endproperty

property property_7; 
@(negedge clk) 
    (!rst && Lflit_id[0] && Nreq && !Sreq) |-> !nextstate[0]; 
endproperty

property property_8; 
@(negedge clk) 
    (!rst && !Lflit_id[0] && !Nflit_id[0] && !Eflit_id[0] && !Wflit_id[0] && !Sflit_id[0] && Lreq && Nreq && !Wreq && !Sreq) |-> !nextstate[0]; 
endproperty

property property_9; 
@(negedge clk) 
    (!rst && !Lflit_id[0] && !Nflit_id[0] && !Eflit_id[0] && !Wflit_id[0] && !Sflit_id[0] && !Lreq && Nreq && Ereq && !Wreq && !Sreq) |-> !nextstate[0]; 
endproperty

property property_10; 
@(negedge clk) 
    (!rst && !Lflit_id[0] && !Nflit_id[0] && !Eflit_id[0] && !Wflit_id[0] && !Sflit_id[0] && !Lreq && !Nreq && Ereq && Wreq && !Sreq) |-> !nextstate[0]; 
endproperty

property property_11; 
@(negedge clk) 
    (!rst && !Lflit_id[0] && !Nflit_id[0] && !Eflit_id[0] && !Wflit_id[0] && !Sflit_id[0] && Nreq && Wreq && !Sreq) |-> !nextstate[0]; 
endproperty

property property_12; 
@(negedge clk) 
    (!rst && !Lreq) |-> !nextstate[1]; 
endproperty

property property_13; 
@(negedge clk) 
    (rst) |-> !nextstate[1]; 
endproperty

property property_14; 
@(negedge clk) 
    (Lflit_id[0] && !Lreq && Nreq && !Ereq) |-> nextstate[2]; 
endproperty

property property_15; 
@(negedge clk) 
    (Lflit_id[0] && Nreq && !Ereq && !Sreq) |-> nextstate[2]; 
endproperty

property property_16; 
@(negedge clk) 
    (!rst && Lflit_id[2] && !Lflit_id[0] && !Nflit_id[0] && !Eflit_id[0] && !Wflit_id[0] && !Sflit_id[0] && Lreq && Nreq && !Wreq) |-> !nextstate[2]; 
endproperty

property property_17; 
@(negedge clk) 
    (!rst && Lflit_id[0] && Lreq && Nreq && !Wreq) |-> !nextstate[2]; 
endproperty

property property_18; 
@(negedge clk) 
    (!rst && !Nreq) |-> !nextstate[2]; 
endproperty

property property_21; 
@(negedge clk) 
    (!rst && Lflit_id[2] && !Lreq && Nreq && Ereq && !Sreq) |-> !nextstate[3]; 
endproperty

property property_22; 
@(negedge clk) 
    (!rst && !Lflit_id[2] && !Nflit_id[2] && !Eflit_id[2] && !Wflit_id[2] && !Sflit_id[2] && !Lreq && Nreq && Ereq && Wreq && !Sreq) |-> !nextstate[3]; 
endproperty

property property_23; 
@(negedge clk) 
    (!rst && !Ereq) |-> !nextstate[3]; 
endproperty

property property_25; 
@(negedge clk) 
    (!rst && !Wreq) |-> !nextstate[4]; 
endproperty

// Assertions

property_0_assert : assert property (property_0) else $error("property_0 not held!");
property_1_assert : assert property (property_1) else $error("property_1 not held!");
property_2_assert : assert property (property_2) else $error("property_2 not held!");
property_3_assert : assert property (property_3) else $error("property_3 not held!");
property_4_assert : assert property (property_4) else $error("property_4 not held!");
property_5_assert : assert property (property_5) else $error("property_5 not held!");
property_6_assert : assert property (property_6) else $error("property_6 not held!");
property_7_assert : assert property (property_7) else $error("property_7 not held!");
property_8_assert : assert property (property_8) else $error("property_8 not held!");
property_9_assert : assert property (property_9) else $error("property_9 not held!");
property_10_assert : assert property (property_10) else $error("property_10 not held!");
property_11_assert : assert property (property_11) else $error("property_11 not held!");
property_12_assert : assert property (property_12) else $error("property_12 not held!");
property_13_assert : assert property (property_13) else $error("property_13 not held!");
property_14_assert : assert property (property_14) else $error("property_14 not held!");
property_15_assert : assert property (property_15) else $error("property_15 not held!");
property_16_assert : assert property (property_16) else $error("property_16 not held!");
property_17_assert : assert property (property_17) else $error("property_17 not held!");
property_18_assert : assert property (property_18) else $error("property_18 not held!");
property_21_assert : assert property (property_21) else $error("property_21 not held!");
property_22_assert : assert property (property_22) else $error("property_22 not held!");
property_23_assert : assert property (property_23) else $error("property_23 not held!");
property_25_assert : assert property (property_25) else $error("property_25 not held!");

  
endmodule
