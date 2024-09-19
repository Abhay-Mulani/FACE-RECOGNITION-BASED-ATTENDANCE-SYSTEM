result,image = cam.read()
        cv2.imshow(inp, image)
        if cv2.waitKey(0):
         cv2.imwrite(inp+".png", image)
         print("image taken")